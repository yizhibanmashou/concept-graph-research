"""Proof-carrying evaluation for finite, positive, function-free Datalog.

This is a semantic layer separate from the frozen gloss-dependency graph. Rules
are universally quantified positive Horn clauses; negation, existential heads,
function symbols, equality, and general FOL are intentionally unsupported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from bisect import insort
from pathlib import Path
from typing import Any


Atom = tuple[str, tuple[str, ...]]
FACT_KNOWLEDGE_PARTITIONS = frozenset({
    "source_assertion",
    "resource_fact",
    "external_assumption",
})


def _parse_atom(value: dict[str, Any], *, ground: bool = False) -> Atom:
    if not isinstance(value, dict) or not isinstance(value.get("predicate"), str) or not value["predicate"]:
        raise ValueError("Atom must have a non-empty string predicate")
    arguments = value.get("arguments", [])
    if not isinstance(arguments, list) or any(not isinstance(x, str) or not x for x in arguments):
        raise ValueError("Atom arguments must be non-empty strings")
    if ground and any(x.startswith("?") for x in arguments):
        raise ValueError("Facts and queries must be ground; variables start with '?' ")
    return value["predicate"], tuple(arguments)


def _atom_json(atom: Atom) -> dict[str, Any]:
    return {"predicate": atom[0], "arguments": list(atom[1])}


def _atom_id(atom: Atom) -> str:
    return json.dumps([atom[0], list(atom[1])], ensure_ascii=False, separators=(",", ":"))


def _vars(atom: Atom) -> set[str]:
    return {term for term in atom[1] if term.startswith("?")}


def _instantiate(atom: Atom, binding: dict[str, str]) -> Atom:
    return atom[0], tuple(binding[t] if t.startswith("?") else t for t in atom[1])


def _constant_domains_by_sort(type_system: dict[str, Any] | None):
    """Index declared constants by every sort they inhabit, including ancestors."""
    if type_system is None:
        return None
    constants = type_system.get("constant_sorts", {})
    parents = type_system.get("sorts", {})
    constants_by_sort: dict[str, set[str]] = {}
    for constant, actual_sorts in constants.items():
        ancestors: set[str] = set()
        pending = list(actual_sorts)
        while pending:
            current = pending.pop()
            if current in ancestors:
                continue
            ancestors.add(current)
            pending.extend(parents.get(current, []))
        for sort in ancestors:
            constants_by_sort.setdefault(sort, set()).add(constant)
    return {sort: frozenset(values) for sort, values in constants_by_sort.items()}


def _allowed_rule_constants(rule: dict[str, Any], type_system: dict[str, Any] | None,
                             constants_by_sort: dict[str, frozenset[str]] | None = None):
    """Return per-variable Herbrand constants admitted by declared sorts."""
    if type_system is None:
        return None
    if constants_by_sort is None:
        constants_by_sort = _constant_domains_by_sort(type_system) or {}
    return {
        variable: constants_by_sort.get(required_sort, frozenset())
        for variable, required_sort in rule.get("variable_sorts", {}).items()
    }


def _binding_allowed(binding: dict[str, str], allowed_constants: dict[str, frozenset[str]] | None) -> bool:
    if allowed_constants is None:
        return True
    return all(binding.get(variable) in constants
               for variable, constants in allowed_constants.items())


def _validate_program(program: dict[str, Any]):
    if not isinstance(program, dict):
        raise ValueError("Program must be a JSON object")
    raw_facts = program.get("facts", [])
    raw_rules = program.get("rules", [])
    if not isinstance(raw_facts, list) or not isinstance(raw_rules, list):
        raise ValueError("facts and rules must be lists")

    facts: dict[Atom, dict[str, Any]] = {}
    for row in raw_facts:
        if not isinstance(row, dict):
            raise ValueError("Each fact must be an object")
        atom = _parse_atom(row, ground=True)
        source_documents = row.get("source_documents", [])
        if not isinstance(source_documents, list) or any(not isinstance(x, str) for x in source_documents):
            raise ValueError("Fact source_documents must be a list of strings")
        knowledge_partition = row.get("knowledge_partition", "unclassified")
        if (not isinstance(knowledge_partition, str)
                or knowledge_partition not in FACT_KNOWLEDGE_PARTITIONS | {"unclassified"}):
            raise ValueError(
                "Fact knowledge_partition must be source_assertion, resource_fact, "
                "external_assumption, or unclassified"
            )
        source_sense_id = row.get("source_sense_id")
        source_gloss_sha256 = row.get("source_gloss_sha256")
        source_claim_refs = row.get("source_claim_refs", [])
        if not isinstance(source_claim_refs, list) or any(
            not isinstance(ref, dict)
            or any(not isinstance(ref.get(field), str) or not ref[field].strip()
                   for field in ("annotation_id", "claim_id", "formula_node_id"))
            for ref in source_claim_refs
        ):
            raise ValueError("Fact source_claim_refs must be a list of annotation/claim/formula-node references")
        if (source_sense_id is None) != (source_gloss_sha256 is None):
            raise ValueError("Fact source_sense_id and source_gloss_sha256 must be provided together")
        if source_sense_id is not None:
            if not isinstance(source_sense_id, str) or not source_sense_id.strip():
                raise ValueError("Fact source_sense_id must be a non-empty string")
            if not isinstance(source_gloss_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", source_gloss_sha256):
                raise ValueError("Fact source_gloss_sha256 must be a 64-character hexadecimal SHA-256")
        facts.setdefault(atom, {
            "atom": _atom_json(atom),
            "source_documents": [],
            "source_bindings": [],
            "source_claim_refs": [],
            "knowledge_partitions": [],
            "partition_was_explicit": False,
        })
        facts[atom]["source_documents"] = sorted(set(facts[atom]["source_documents"] + source_documents))
        for source_claim_ref in source_claim_refs:
            if source_claim_ref not in facts[atom]["source_claim_refs"]:
                facts[atom]["source_claim_refs"].append(source_claim_ref)
        facts[atom]["source_claim_refs"].sort(
            key=lambda item: (item["annotation_id"], item["claim_id"], item["formula_node_id"])
        )
        if source_sense_id is not None:
            source_binding = {
                "sense_id": source_sense_id,
                "gloss_sha256": source_gloss_sha256.lower(),
                "source_documents": sorted(set(source_documents)),
            }
            if source_binding not in facts[atom]["source_bindings"]:
                facts[atom]["source_bindings"].append(source_binding)
                facts[atom]["source_bindings"].sort(
                    key=lambda item: (item["sense_id"], item["gloss_sha256"], item["source_documents"])
                )
        facts[atom]["knowledge_partitions"] = sorted(set(
            facts[atom]["knowledge_partitions"] + [knowledge_partition]
        ))
        facts[atom]["partition_was_explicit"] |= "knowledge_partition" in row

    rules: dict[str, dict[str, Any]] = {}
    for row in raw_rules:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError("Each rule must have a non-empty unique id")
        rid = row["id"]
        if rid in rules:
            raise ValueError(f"Duplicate rule id: {rid}")
        head = _parse_atom(row.get("head", {}))
        body_raw = row.get("body")
        if not isinstance(body_raw, list):
            raise ValueError(f"Rule {rid}: body must be a list")
        body = [_parse_atom(atom) for atom in body_raw]
        body_vars = set().union(*(_vars(atom) for atom in body)) if body else set()
        if not _vars(head) <= body_vars:
            raise ValueError(f"Rule {rid}: unsafe head variable (not bound in body)")
        provenance = row.get("provenance", {})
        if not isinstance(provenance, dict):
            raise ValueError(f"Rule {rid}: provenance must be an object")
        rule_record = {"id": rid, "head": head, "body": body, "provenance": provenance}
        type_system = program.get("type_system")
        if isinstance(type_system, dict):
            variable_sorts = row.get("variable_sorts")
            if variable_sorts is None:
                table = type_system.get("rule_variable_sorts", {})
                if isinstance(table, dict):
                    variable_sorts = table.get(rid)
            if variable_sorts is not None:
                rule_record["variable_sorts"] = variable_sorts
        rules[rid] = rule_record

    raw_query = program.get("query")
    query = _parse_atom(raw_query, ground=True)
    signatures: dict[str, int] = {}
    atoms = list(facts) + [query]
    for rule in rules.values():
        atoms.append(rule["head"])
        atoms.extend(rule["body"])
    for predicate, arguments in atoms:
        if predicate in signatures and signatures[predicate] != len(arguments):
            raise ValueError(f"Predicate {predicate} used with inconsistent arity")
        signatures[predicate] = len(arguments)
    if "type_system" in program:
        from src.logic.typed_program_validator import validate_typed_program

        type_report = validate_typed_program(program)
        if not type_report["valid"]:
            errors = "; ".join(type_report["errors"][:8])
            raise ValueError(f"Typed Datalog program is invalid: {errors}")
    return facts, rules, query


def _unify(pattern: Atom, fact: Atom, binding: dict[str, str]) -> dict[str, str] | None:
    if pattern[0] != fact[0] or len(pattern[1]) != len(fact[1]):
        return None
    result = dict(binding)
    for term, value in zip(pattern[1], fact[1]):
        if term.startswith("?"):
            if term in result and result[term] != value:
                return None
            result[term] = value
        elif term != value:
            return None
    return result


def _matches_body(body: list[Atom], known_by_predicate: dict[str, list[Atom]],
                  allowed_constants: dict[str, frozenset[str]] | None = None):
    if not body:
        if _binding_allowed({}, allowed_constants):
            yield {}, []
        return

    def extend(index: int, binding: dict[str, str], premises: list[Atom]):
        if index == len(body):
            if _binding_allowed(binding, allowed_constants):
                yield binding, premises
            return
        pattern = body[index]
        for fact in known_by_predicate.get(pattern[0], []):
            updated = _unify(pattern, fact, binding)
            if updated is not None:
                yield from extend(index + 1, updated, premises + [fact])

    yield from extend(0, {}, [])


def build_closure(program: dict[str, Any]):
    """Materialize the least Herbrand model and one provenance derivation/fact."""
    facts, rules, query = _validate_program(program)
    known = dict(facts)
    known_by_predicate: dict[str, list[Atom]] = {}
    for atom in sorted(known):
        known_by_predicate.setdefault(atom[0], []).append(atom)
    derivations: dict[Atom, dict[str, Any]] = {}
    type_system = program.get("type_system")
    constants_by_sort = _constant_domains_by_sort(type_system)
    allowed_constants_by_rule = {
        rid: _allowed_rule_constants(rule, type_system, constants_by_sort)
        for rid, rule in rules.items()
    }
    changed = True
    while changed:
        changed = False
        for rid in sorted(rules):
            rule = rules[rid]
            for binding, premises in _matches_body(
                rule["body"], known_by_predicate, allowed_constants_by_rule[rid]
            ):
                head = _instantiate(rule["head"], binding)
                if head not in known:
                    known[head] = {"atom": _atom_json(head), "source_documents": []}
                    insort(known_by_predicate.setdefault(head[0], []), head)
                    derivations[head] = {"rule_id": rid, "binding": dict(sorted(binding.items())), "premises": premises}
                    changed = True
    return facts, rules, query, known, derivations


def make_certificate(query: Atom, facts: dict[Atom, dict[str, Any]], rules: dict[str, dict[str, Any]],
                     derivations: dict[Atom, dict[str, Any]],
                     type_system_sha256: str | None = None):
    nodes: dict[str, dict[str, Any]] = {}
    active: set[Atom] = set()

    def visit(atom: Atom):
        node_id = _atom_id(atom)
        if node_id in nodes:
            return node_id
        if atom in active:
            raise ValueError(f"Cycle in proof provenance at {_atom_json(atom)}")
        active.add(atom)
        if atom in facts:
            node = {"node_id": node_id, "atom": _atom_json(atom), "kind": "fact",
                    "source_documents": facts[atom]["source_documents"],
                    "source_bindings": facts[atom]["source_bindings"],
                    "source_claim_refs": facts[atom]["source_claim_refs"]}
            if facts[atom]["partition_was_explicit"]:
                node["knowledge_partitions"] = facts[atom]["knowledge_partitions"]
        elif atom in derivations:
            derivation = derivations[atom]
            rule = rules[derivation["rule_id"]]
            premise_ids = [visit(premise) for premise in derivation["premises"]]
            node = {"node_id": node_id, "atom": _atom_json(atom), "kind": "rule",
                    "rule_id": derivation["rule_id"], "binding": derivation["binding"],
                    "premise_node_ids": premise_ids, "provenance": rule["provenance"]}
        else:
            raise ValueError(f"No derivation for {_atom_json(atom)}")
        active.remove(atom)
        nodes[node_id] = node
        return node_id

    root = visit(query)
    certificate = {"root": root, "nodes": list(nodes.values())}
    if type_system_sha256 is not None:
        certificate["type_system_sha256"] = type_system_sha256
    return certificate


def verify_certificate(program: dict[str, Any], certificate: dict[str, Any]) -> bool:
    """Independently check each fact/rule application and all premise links."""
    facts, rules, query = _validate_program(program)
    type_system = program.get("type_system")
    constants_by_sort = _constant_domains_by_sort(type_system)
    allowed_constants_by_rule = {
        rid: _allowed_rule_constants(rule, type_system, constants_by_sort)
        for rid, rule in rules.items()
    }
    if not isinstance(certificate, dict) or not isinstance(certificate.get("nodes"), list):
        return False
    expected_type_hash = None
    if "type_system" in program:
        from src.logic.typed_program_validator import validate_typed_program

        expected_type_hash = validate_typed_program(program).get("signature_table_sha256")
    if expected_type_hash is not None:
        if certificate.get("type_system_sha256") != expected_type_hash:
            return False
    elif "type_system_sha256" in certificate:
        return False
    raw_nodes = certificate["nodes"]
    if any(not isinstance(node, dict) or not isinstance(node.get("node_id"), str) for node in raw_nodes):
        return False
    nodes = {node["node_id"]: node for node in raw_nodes}
    if len(nodes) != len(raw_nodes) or certificate.get("root") != _atom_id(query):
        return False
    visiting: set[str] = set()
    checked: set[str] = set()

    def check(node_id: str) -> bool:
        if node_id in checked:
            return True
        if node_id in visiting or node_id not in nodes:
            return False
        visiting.add(node_id)
        node = nodes[node_id]
        try:
            atom = _parse_atom(node.get("atom", {}), ground=True)
        except (TypeError, ValueError):
            return False
        if _atom_id(atom) != node_id:
            return False
        if node.get("kind") == "fact":
            valid = (
                atom in facts
                and node.get("source_documents", []) == facts[atom]["source_documents"]
                and node.get("source_bindings", []) == facts[atom]["source_bindings"]
                and node.get("source_claim_refs", []) == facts[atom]["source_claim_refs"]
            )
            if valid and "knowledge_partitions" in node:
                valid = (
                    facts[atom]["partition_was_explicit"]
                    and node["knowledge_partitions"] == facts[atom]["knowledge_partitions"]
                )
            elif valid and facts[atom]["partition_was_explicit"]:
                valid = False
        elif node.get("kind") == "rule":
            rule = rules.get(node.get("rule_id"))
            binding = node.get("binding")
            premise_ids = node.get("premise_node_ids")
            valid = isinstance(rule, dict) and isinstance(binding, dict) and isinstance(premise_ids, list)
            if valid:
                try:
                    rule_vars = set().union(_vars(rule["head"]), *(_vars(atom) for atom in rule["body"]))
                    valid = (set(binding) == rule_vars
                             and all(isinstance(k, str) and k.startswith("?") and isinstance(v, str) and v
                                     and not v.startswith("?") for k, v in binding.items()))
                    valid = valid and _binding_allowed(binding, allowed_constants_by_rule.get(rule["id"]))
                    head = _instantiate(rule["head"], binding)
                    premises = [_instantiate(body_atom, binding) for body_atom in rule["body"]]
                    valid = (valid and head == atom and node.get("provenance") == rule["provenance"]
                             and len(premises) == len(premise_ids)
                             and all(premise_ids[i] == _atom_id(premises[i]) and check(premise_ids[i])
                                     for i in range(len(premises))))
                except (KeyError, TypeError):
                    valid = False
        else:
            valid = False
        visiting.remove(node_id)
        if valid:
            checked.add(node_id)
        return valid

    root = certificate.get("root", "")
    return check(root) and checked == set(nodes)


def make_countermodel(known: dict[Atom, dict[str, Any]], query: Atom,
                      type_system_sha256: str | None = None) -> dict[str, Any]:
    """Serialize a finite Herbrand interpretation falsifying the query."""
    interpretation = [_atom_json(atom) for atom in sorted(known)]
    canonical = json.dumps(interpretation, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    countermodel = {
        "kind": "finite_herbrand_model",
        "interpretation": interpretation,
        "query_absent": query not in known,
        "interpretation_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
    if type_system_sha256 is not None:
        countermodel["type_system_sha256"] = type_system_sha256
    return countermodel


def verify_countermodel(program: dict[str, Any], countermodel: dict[str, Any]) -> bool:
    """Check that a finite interpretation satisfies the program and falsifies query.

    The verifier checks model satisfaction directly, independent of the closure
    implementation. A model of the rules in which the query is false is a
    counterexample to entailment within this function-free positive fragment.
    """
    try:
        facts, rules, query = _validate_program(program)
        expected_type_hash = None
        if "type_system" in program:
            from src.logic.typed_program_validator import validate_typed_program

            expected_type_hash = validate_typed_program(program).get("signature_table_sha256")
        if (not isinstance(countermodel, dict)
                or countermodel.get("kind") != "finite_herbrand_model"
                or countermodel.get("query_absent") is not True
                or not isinstance(countermodel.get("interpretation"), list)):
            return False
        if expected_type_hash is not None:
            if countermodel.get("type_system_sha256") != expected_type_hash:
                return False
        elif "type_system_sha256" in countermodel:
            return False
        raw_interpretation = countermodel["interpretation"]
        atoms = [_parse_atom(row, ground=True) for row in raw_interpretation]
        if (len(atoms) != len(set(atoms)) or atoms != sorted(atoms)
                or raw_interpretation != [_atom_json(atom) for atom in atoms]):
            return False
        if "type_system" in program:
            from src.logic.typed_program_validator import validate_typed_program

            typed_model_program = {**program, "facts": raw_interpretation}
            if not validate_typed_program(typed_model_program)["valid"]:
                return False
        canonical = json.dumps(raw_interpretation, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if countermodel.get("interpretation_sha256") != expected_hash:
            return False
        model = set(atoms)
        if query in model or not set(facts) <= model:
            return False

        signatures: dict[str, int] = {}
        constants = set()
        for atom in list(facts) + [query]:
            signatures[atom[0]] = len(atom[1])
            constants.update(term for term in atom[1] if not term.startswith("?"))
        for rule in rules.values():
            for atom in (rule["head"], *rule["body"]):
                signatures[atom[0]] = len(atom[1])
                constants.update(term for term in atom[1] if not term.startswith("?"))
        for atom in atoms:
            if signatures.get(atom[0]) != len(atom[1]) or any(term not in constants for term in atom[1]):
                return False

        by_predicate: dict[str, list[Atom]] = {}
        for atom in atoms:
            by_predicate.setdefault(atom[0], []).append(atom)
        type_system = program.get("type_system")
        constants_by_sort = _constant_domains_by_sort(type_system)
        for rule in rules.values():
            allowed_constants = _allowed_rule_constants(rule, type_system, constants_by_sort)
            for binding, _ in _matches_body(rule["body"], by_predicate, allowed_constants):
                if _instantiate(rule["head"], binding) not in model:
                    return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


def verify_query(program: dict[str, Any]):
    type_report = None
    if isinstance(program, dict) and "type_system" in program:
        from src.logic.typed_program_validator import validate_typed_program

        type_report = validate_typed_program(program)
    facts, rules, query, known, derivations = build_closure(program)
    if query in known:
        certificate = make_certificate(
            query, facts, rules, derivations,
            type_report.get("signature_table_sha256") if type_report is not None else None,
        )
        result = {"status": "entailed_in_positive_datalog", "query": _atom_json(query),
                  "certificate": certificate,
                  "certificate_valid": verify_certificate(program, certificate)}
        if type_report is not None:
            result["type_validation"] = type_report
        return result
    countermodel = make_countermodel(
        known, query,
        type_report.get("signature_table_sha256") if type_report is not None else None,
    )
    result = {"status": "not_entailed_in_least_herbrand_model", "query": _atom_json(query),
              "countermodel": countermodel,
              "countermodel_valid": verify_countermodel(program, countermodel),
              "scope_note": "Non-entailment is relative to this finite positive Datalog program; it says nothing about omitted/background knowledge."}
    if type_report is not None:
        result["type_validation"] = type_report
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path, help="JSON file with facts, rules, and a ground query")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    program = json.loads(args.program.read_text(encoding="utf-8"))
    result = verify_query(program)
    if result.get("certificate") and not result["certificate_valid"]:
        raise SystemExit("Internal proof-certificate verification failed")
    if result.get("countermodel") and not result["countermodel_valid"]:
        raise SystemExit("Internal countermodel verification failed")
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
