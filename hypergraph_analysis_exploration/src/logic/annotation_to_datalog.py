"""Compile guarded reviewed gloss annotations to positive Datalog.

Schemas through 0.6 use the legacy unary shared-variable fragment. Schema 0.7
adds explicit target-variable annotations and safe multivariate positive rules.
The compiler preserves claim direction and rejects unsupported semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any

from src.logic.annotation_validator import load_jsonl, validate_dataset


COMPILER_VERSION = "annotation-to-positive-horn/6"
MAX_DNF_BRANCHES = 64
MIN_COMPILATION_CONFIDENCE = "medium"
SOURCE_GROUNDED_INFERENCE_BASES = {
    "lexical_or_paraphrastic",
    "compositional_or_logical",
}
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _formula_conjuncts(formula_id: str, nodes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    node = nodes.get(formula_id)
    if not isinstance(node, dict):
        raise ValueError(f"missing formula node {formula_id}")
    kind = node.get("kind")
    if kind == "atom":
        return [node]
    if kind == "and":
        children = node.get("children")
        if not isinstance(children, list) or len(children) < 2:
            raise ValueError(f"AND node {formula_id} must have at least two children")
        result = []
        for child_id in children:
            result.extend(_formula_conjuncts(child_id, nodes))
        return result
    raise ValueError(f"OR/unsupported operator {kind!r} cannot be represented in target-to-gloss Horn direction")


def _formula_dnf(formula_id: str, nodes: dict[str, dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Represent positive AND/OR formulas as DNF branches for body-to-head rules."""
    node = nodes.get(formula_id)
    if not isinstance(node, dict):
        raise ValueError(f"missing formula node {formula_id}")
    kind = node.get("kind")
    if kind == "atom":
        return [[node]]
    children = node.get("children")
    if kind not in {"and", "or"} or not isinstance(children, list) or len(children) < 2:
        raise ValueError(f"unsupported formula operator {kind!r}; only atom/AND/OR is supported")
    child_branches = [_formula_dnf(child_id, nodes) for child_id in children]
    if kind == "or":
        branch_count = sum(len(group) for group in child_branches)
        if branch_count > MAX_DNF_BRANCHES:
            raise ValueError(f"AND/OR expansion exceeds the {MAX_DNF_BRANCHES}-branch safety limit")
        branches = [branch for group in child_branches for branch in group]
    else:
        branch_count = 1
        for group in child_branches:
            branch_count *= len(group)
            if branch_count > MAX_DNF_BRANCHES:
                raise ValueError(f"AND/OR expansion exceeds the {MAX_DNF_BRANCHES}-branch safety limit")
        branches = [
            [atom for group in choice for atom in group]
            for choice in product(*child_branches)
        ]
    if len(branches) > MAX_DNF_BRANCHES:
        raise ValueError(f"AND/OR expansion exceeds the {MAX_DNF_BRANCHES}-branch safety limit")
    return branches


def _normalize_unary_atoms(nodes: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    variable = None
    atoms = []
    for node in nodes:
        arguments = node.get("arguments")
        if not isinstance(arguments, list) or len(arguments) != 1:
            raise ValueError(f"predicate {node.get('predicate')!r} must be unary in compiler v1")
        term = arguments[0]
        if not isinstance(term, dict) or term.get("kind") != "variable":
            raise ValueError("only a variable argument is supported; constants/relations require a richer compiler")
        candidate = term.get("id")
        if not isinstance(candidate, str) or not candidate.startswith("?") or len(candidate) < 2:
            raise ValueError("AST variable IDs must start with '?' and contain a name")
        if variable is not None and candidate != variable:
            raise ValueError("all formula atoms must share one target variable in compiler v1")
        variable = candidate
        atoms.append({"predicate": node["predicate"], "arguments": [candidate]})
    if variable is None:
        raise ValueError("formula has no atom")
    return variable, atoms


def _normalize_relational_atoms(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize schema-0.7 atoms while preserving variable/constant terms."""
    atoms = []
    for node in nodes:
        arguments = node.get("arguments")
        if not isinstance(arguments, list) or not arguments:
            raise ValueError(f"predicate {node.get('predicate')!r} must have at least one argument")
        terms = []
        for term in arguments:
            if not isinstance(term, dict) or term.get("kind") not in {"variable", "constant"}:
                raise ValueError("only variable and constant arguments are supported")
            identifier = term.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise ValueError("atom argument IDs must be non-empty strings")
            if term["kind"] == "variable":
                if not identifier.startswith("?") or len(identifier) < 2:
                    raise ValueError("AST variable IDs must start with '?' and contain a name")
            elif identifier.startswith("?"):
                raise ValueError("constant IDs cannot start with '?' because Datalog reserves that prefix for variables")
            terms.append(identifier)
        atoms.append({"predicate": node["predicate"], "arguments": terms})
    return atoms


def _rule_variables(head: dict[str, Any], body: list[dict[str, Any]]) -> set[str]:
    return {
        term
        for atom in [head, *body]
        for term in atom["arguments"]
        if term.startswith("?")
    }


def _rule(rule_id: str, head: dict[str, Any], body: list[dict[str, Any]], provenance: dict[str, Any],
          variable_sorts: dict[str, str] | None = None):
    rule = {"id": rule_id, "head": head, "body": body, "provenance": provenance}
    if variable_sorts is not None:
        rule["variable_sorts"] = dict(sorted(variable_sorts.items()))
    return rule


def compile_annotations(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return compiled rules and per-claim rejections for canonical annotations."""
    errors = validate_dataset(records)
    if not records:
        raise ValueError("no annotation records provided")
    if errors:
        raise ValueError("input annotation records are invalid: " + "; ".join(errors[:8]))
    rules = []
    rejections = []
    for record in records:
        annotation_id = record["annotation_id"]
        analysis = record["analysis"]
        if analysis["status"] != "annotated":
            rejections.append({"annotation_id": annotation_id, "claim_id": None,
                               "reason": f"analysis status {analysis['status']!r} is not compiled"})
            continue
        nodes = {node["id"]: node for node in analysis["nodes"]}
        if not analysis["rule_claims"]:
            rejections.append({"annotation_id": annotation_id, "claim_id": None,
                               "reason": "annotated record has no directional rule claims"})
            continue
        for claim in analysis["rule_claims"]:
            base_rejection = {"annotation_id": annotation_id, "claim_id": claim["id"]}
            if claim["semantic_support"] != "supported":
                rejections.append({**base_rejection,
                                   "reason": f"semantic support is {claim['semantic_support']!r}; only explicitly supported claims are compiled"})
                continue
            if (record["schema_version"] in {"0.4-draft", "0.5-draft", "0.6-draft", "0.7-draft"}
                    and (not claim["inference_basis"]
                         or not set(claim["inference_basis"]) <= SOURCE_GROUNDED_INFERENCE_BASES)):
                rejected_bases = sorted(set(claim["inference_basis"]) - SOURCE_GROUNDED_INFERENCE_BASES)
                reason = (
                    "inference basis is empty"
                    if not claim["inference_basis"]
                    else "inference basis is not gloss-grounded: " + ", ".join(rejected_bases)
                )
                rejections.append({
                    **base_rejection,
                    "reason": reason,
                })
                continue
            if claim["confidence"] == "low":
                rejections.append({**base_rejection,
                                   "reason": f"claim confidence 'low' is below compilation threshold '{MIN_COMPILATION_CONFIDENCE}'"})
                continue
            if claim["relation"] not in {"necessary", "sufficient", "biconditional"}:
                rejections.append({**base_rejection, "reason": f"claim relation {claim['relation']!r} is not a definition rule"})
                continue
            valid_directions = {
                "necessary": "target_to_gloss",
                "sufficient": "gloss_to_target",
                "biconditional": "both",
            }
            if claim["direction"] != valid_directions[claim["relation"]]:
                rejections.append({**base_rejection,
                                   "reason": "relation/direction mismatch; explicit compatible direction required"})
                continue
            variable_sort_judgments = None
            if record["schema_version"] in {"0.6-draft", "0.7-draft"}:
                variable_sort_judgments = claim["variable_sort_judgments"]
                unresolved = sorted(
                    variable for variable, judgment in variable_sort_judgments.items()
                    if judgment["status"] != "assigned"
                )
                if unresolved:
                    rejections.append({
                        **base_rejection,
                        "reason": "variable sort judgment unresolved for " + ", ".join(unresolved),
                    })
                    continue
                variable_sorts = {
                    variable: judgment["sort"]
                    for variable, judgment in variable_sort_judgments.items()
                }
            elif record["schema_version"] == "0.5-draft":
                variable_sorts = claim["variable_sorts"]
            else:
                variable_sorts = None
            sense_id = record["sense"]["synset_id"]
            evidence = claim["evidence_spans"]
            source = record["source"]
            provenance_base = {
                "annotation_id": annotation_id,
                "claim_id": claim["id"],
                "annotation_schema_version": record["schema_version"],
                "sense_id": sense_id,
                "lemma": record["sense"]["lemmas"],
                "pos": record["sense"]["pos"],
                "source_resource": source["resource"],
                "source_version": source["version"],
                "source_record_id": source["record_id"],
                "source_gloss_sha256": source["input_sha256"],
                "source_records": record.get("provenance", {}).get("source_records", []),
                "nli_hypothesis_sha256": claim.get("nli_hypothesis_sha256"),
                "formula_node_id": claim["formula_node_id"],
                "evidence_spans": evidence,
                "relation": claim["relation"],
                "direction": claim["direction"],
                "semantic_support": claim["semantic_support"],
                "inference_basis": claim.get("inference_basis"),
                "support_confidence": claim["confidence"],
                "compiler_version": COMPILER_VERSION,
            }
            if record["schema_version"] == "0.7-draft":
                provenance_base["target_variable"] = claim["target_variable"]
            if variable_sort_judgments is not None:
                provenance_base["variable_sort_judgments"] = variable_sort_judgments
                provenance_base["variable_sort_review_status"] = record["annotation"]["adjudication_status"]
            prefix = f"{annotation_id}:{claim['id']}"
            compiled = []
            if claim["relation"] in {"necessary", "biconditional"}:
                try:
                    forward_nodes = _formula_conjuncts(claim["formula_node_id"], nodes)
                    target_variable = claim.get("target_variable")
                    if record["schema_version"] == "0.7-draft":
                        forward_atoms = _normalize_relational_atoms(forward_nodes)
                        for atom in forward_atoms:
                            unexpected = {term for term in atom["arguments"] if term.startswith("?")} - {target_variable}
                            if unexpected:
                                raise ValueError(
                                    "necessary-direction atom has non-target head variable(s) "
                                    + ", ".join(sorted(unexpected))
                                    + "; existential heads are outside safe positive Datalog"
                                )
                        variable = target_variable
                    else:
                        variable, forward_atoms = _normalize_unary_atoms(forward_nodes)
                    target = {"predicate": f"wn_sense:{sense_id}", "arguments": [variable]}
                    for atom_index, atom in enumerate(forward_atoms):
                        provenance = {**provenance_base, "projection": "target_to_gloss",
                                      "formula_atom_index": atom_index}
                        rule_sorts = variable_sorts
                        if record["schema_version"] == "0.7-draft":
                            rule_sorts = {key: value for key, value in variable_sorts.items()
                                          if key in _rule_variables(atom, [target])}
                        compiled.append(_rule(
                            f"{prefix}:necessary:{atom_index}", atom, [target], provenance, rule_sorts
                        ))
                except ValueError as exc:
                    rejections.append({**base_rejection, "projection": "target_to_gloss", "reason": str(exc)})
            if claim["relation"] in {"sufficient", "biconditional"}:
                try:
                    branches = _formula_dnf(claim["formula_node_id"], nodes)
                    normalized_branches = []
                    target_variable = claim.get("target_variable")
                    if record["schema_version"] == "0.7-draft":
                        for branch in branches:
                            branch_atoms = _normalize_relational_atoms(branch)
                            branch_variables = {
                                term for atom in branch_atoms for term in atom["arguments"]
                                if term.startswith("?")
                            }
                            if target_variable not in branch_variables:
                                raise ValueError(
                                    f"sufficient-direction DNF branch does not contain target_variable {target_variable!r}"
                                )
                            normalized_branches.append(branch_atoms)
                        shared_variable = target_variable
                    else:
                        shared_variable = None
                        for branch in branches:
                            branch_variable, branch_atoms = _normalize_unary_atoms(branch)
                            if shared_variable is not None and branch_variable != shared_variable:
                                raise ValueError("all OR branches must share the same target variable")
                            shared_variable = branch_variable
                            normalized_branches.append(branch_atoms)
                    target = {"predicate": f"wn_sense:{sense_id}", "arguments": [shared_variable]}
                    for branch_index, branch_atoms in enumerate(normalized_branches):
                        provenance = {**provenance_base, "projection": "gloss_to_target",
                                      "formula_branch_index": branch_index}
                        rule_sorts = variable_sorts
                        if record["schema_version"] == "0.7-draft":
                            rule_sorts = {key: value for key, value in variable_sorts.items()
                                          if key in _rule_variables(target, branch_atoms)}
                        compiled.append(_rule(
                            f"{prefix}:sufficient:{branch_index}", target, branch_atoms, provenance, rule_sorts
                        ))
                except ValueError as exc:
                    rejections.append({**base_rejection, "projection": "gloss_to_target", "reason": str(exc)})
            rules.extend(compiled)

    return {
        "compiler_version": COMPILER_VERSION,
        "supported_fragment": "schemas 0.2-0.6: unary positive predicates over one shared variable; schema 0.7: explicitly targeted positive multi-argument predicates with safe necessary atom/AND heads and sufficient atom/AND/OR bounded DNF bodies (max 64 branches)",
        "minimum_compilation_confidence": MIN_COMPILATION_CONFIDENCE,
        "compiled_rule_count": len(rules),
        "rejection_count": len(rejections),
        "rules": rules,
        "rejections": rejections,
        "interpretation_limit": "compiled rules are formalizations of claims explicitly judged supported by annotators; a proof checker verifies derivations from these rules but does not establish that the annotations faithfully express the source gloss",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotations", type=Path, help="canonical annotation JSONL from one or more annotators")
    parser.add_argument("--output", type=Path, required=True, help="compiled rule-library JSON")
    parser.add_argument("--strict", action="store_true", help="fail without writing if any claim is rejected")
    parser.add_argument("--force", action="store_true", help="replace an existing output")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        records, _, parse_errors = load_jsonl(args.annotations)
        if parse_errors:
            raise ValueError("invalid annotation JSONL: " + "; ".join(parse_errors[:5]))
        compiled = compile_annotations(records)
        if args.strict and compiled["rejections"]:
            raise ValueError(f"strict mode rejected {compiled['rejection_count']} unsupported claim(s); no output written")
        compiled["input_hashes"] = {
            "annotation_jsonl_sha256": hashlib.sha256(args.annotations.read_bytes()).hexdigest()
        }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(compiled, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"Compiled {compiled['compiled_rule_count']} positive Horn rule(s); rejected {compiled['rejection_count']} claim(s)")
    print(f"Rule library: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
