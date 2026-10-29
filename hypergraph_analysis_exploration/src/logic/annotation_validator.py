"""Validate JSONL WordNet gloss annotations and dataset split hygiene.

Character spans use Python Unicode code-point offsets, end-exclusive. This
validator checks annotation structure only; it does not judge semantic truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


POS_VALUES = {"n", "v", "a", "r"}
ANALYSIS_STATUSES = {
    "annotated", "ambiguous", "underspecified", "unsupported", "needs_review",
    "not_a_definition", "source_unclear",
}
NODE_KINDS = {"atom", "and", "or", "not", "forall", "exists", "implies", "unknown"}
CLAIM_RELATIONS = {"necessary", "sufficient", "biconditional", "typical", "example", "other"}
CLAIM_DIRECTIONS = {"target_to_gloss", "gloss_to_target", "both", "none"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
SEMANTIC_SUPPORT_VALUES = {"supported", "not_supported", "uncertain", "unassessed"}
INFERENCE_BASIS_VALUES = {
    "lexical_or_paraphrastic", "compositional_or_logical",
    "external_world_knowledge", "pragmatic_or_conversational",
    "figurative_or_metaphorical", "unclear", "unassessed",
}
SUPPORT_REASON_VALUES = {
    "content_not_licensed", "claim_overstates_or_omits_qualifier",
    "direction_mismatch", "operator_or_scope_mismatch", "source_conflict",
    "lexical_or_sense_ambiguity", "scope_or_reference_ambiguity",
    "insufficient_context", "other",
}
VARIABLE_SORT_BASES = {"gloss_span", "lexical_semantics", "resource_relation", "reviewer_convention", "unknown"}
NOT_SUPPORTED_REASON_VALUES = {
    "content_not_licensed", "claim_overstates_or_omits_qualifier",
    "direction_mismatch", "operator_or_scope_mismatch", "source_conflict", "other",
}
UNCERTAIN_REASON_VALUES = {
    "lexical_or_sense_ambiguity", "scope_or_reference_ambiguity",
    "insufficient_context", "other",
}
PROJECTION_STATUSES = {"projectable", "partial", "unsupported", "not_attempted"}
ADJUDICATION_STATUSES = {"independent", "adjudicated", "unresolved"}
SPLIT_VALUES = {"train", "dev", "test", "unassigned"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _is_variable_id(value: Any) -> bool:
    """The annotation grammar uses ?name IDs for variables (including binders)."""
    return isinstance(value, str) and value.startswith("?") and len(value) > 1


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_enum(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def _check_span(span: Any, gloss: str, where: str, errors: list[str]) -> None:
    if not isinstance(span, dict):
        errors.append(f"{where}: span must be an object")
        return
    start, end = span.get("start"), span.get("end")
    if type(start) is not int or type(end) is not int:
        errors.append(f"{where}: span start/end must be integers")
        return
    if start < 0 or end <= start or end > len(gloss):
        errors.append(f"{where}: expected 0 <= start < end <= gloss length ({len(gloss)} code points)")


def _valid_span_bounds(span: Any, gloss_length: int) -> tuple[int, int] | None:
    if not isinstance(span, dict):
        return None
    start, end = span.get("start"), span.get("end")
    if type(start) is not int or type(end) is not int:
        return None
    if start < 0 or end <= start or end > gloss_length:
        return None
    return start, end


def _span_covered_by_union(target: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    """Return whether valid half-open spans cover the target without gaps."""
    cursor = target[0]
    for start, end in sorted(spans):
        if end <= cursor:
            continue
        if start > cursor:
            return False
        cursor = max(cursor, end)
        if cursor >= target[1]:
            return True
    return False


def validate_record(record: Any) -> list[str]:
    """Return all detectable structural errors in one annotation record."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]

    schema_version = record.get("schema_version")
    if not isinstance(schema_version, str) or schema_version not in {
        "0.2-draft", "0.3-draft", "0.4-draft", "0.5-draft", "0.6-draft", "0.7-draft"
    }:
        errors.append("schema_version must be one of '0.2-draft' through '0.7-draft'")
    for key in ("item_id", "annotation_id"):
        if not _is_nonempty_string(record.get(key)):
            errors.append(f"{key} must be a non-empty string")

    source = record.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
        source = {}
    for key in ("resource", "version", "record_id", "license"):
        if not _is_nonempty_string(source.get(key)):
            errors.append(f"source.{key} must be a non-empty string")
    input_sha256 = source.get("input_sha256")
    if not isinstance(input_sha256, str) or not SHA256_RE.fullmatch(input_sha256):
        errors.append("source.input_sha256 must be a 64-character hexadecimal SHA-256")

    if "provenance" in record:
        provenance = record.get("provenance")
        if not isinstance(provenance, dict):
            errors.append("provenance must be an object when supplied")
        elif "source_records" in provenance:
            source_records = provenance.get("source_records")
            if not isinstance(source_records, list) or not source_records:
                errors.append("provenance.source_records must be a non-empty list when supplied")
            else:
                for index, source_record in enumerate(source_records):
                    where = f"provenance.source_records[{index}]"
                    if not isinstance(source_record, dict):
                        errors.append(f"{where} must be an object")
                        continue
                    if not _is_nonempty_string(source_record.get("path")):
                        errors.append(f"{where}.path must be a non-empty string")
                    source_hash = source_record.get("sha256")
                    if not isinstance(source_hash, str) or not SHA256_RE.fullmatch(source_hash):
                        errors.append(f"{where}.sha256 must be a 64-character hexadecimal SHA-256")

    sense = record.get("sense")
    if not isinstance(sense, dict):
        errors.append("sense must be an object")
        sense = {}
    for key in ("synset_id", "gloss"):
        if not _is_nonempty_string(sense.get(key)):
            errors.append(f"sense.{key} must be a non-empty string")
    lemmas = sense.get("lemmas")
    if not isinstance(lemmas, list) or not lemmas or any(not _is_nonempty_string(x) for x in lemmas):
        errors.append("sense.lemmas must be a non-empty list of non-empty strings")
    if not _is_enum(sense.get("pos"), POS_VALUES):
        errors.append(f"sense.pos must be one of {sorted(POS_VALUES)}")
    gloss = sense.get("gloss") if isinstance(sense.get("gloss"), str) else ""
    if isinstance(input_sha256, str) and SHA256_RE.fullmatch(input_sha256) and _is_nonempty_string(gloss):
        expected_sha256 = hashlib.sha256(gloss.encode("utf-8")).hexdigest()
        if input_sha256.lower() != expected_sha256:
            errors.append("source.input_sha256 does not match UTF-8 SHA-256 of sense.gloss")

    analysis = record.get("analysis")
    if not isinstance(analysis, dict):
        errors.append("analysis must be an object")
        analysis = {}
    if not _is_enum(analysis.get("status"), ANALYSIS_STATUSES):
        errors.append(f"analysis.status must be one of {sorted(ANALYSIS_STATUSES)}")

    raw_nodes = analysis.get("nodes")
    if not isinstance(raw_nodes, list):
        errors.append("analysis.nodes must be a list")
        raw_nodes = []
    nodes: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(raw_nodes):
        where = f"analysis.nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{where} must be an object")
            continue
        node_id = node.get("id")
        if not _is_nonempty_string(node_id):
            errors.append(f"{where}.id must be a non-empty string")
            continue
        if node_id in nodes:
            errors.append(f"duplicate AST node id: {node_id}")
            continue
        nodes[node_id] = node
        kind = node.get("kind")
        if not _is_enum(kind, NODE_KINDS):
            errors.append(f"{where}.kind must be one of {sorted(NODE_KINDS)}")
        _check_span(node.get("span"), gloss, f"{where}.span", errors)
        if kind == "atom":
            if not _is_nonempty_string(node.get("predicate")):
                errors.append(f"{where}.predicate must be a non-empty string")
            args = node.get("arguments")
            if not isinstance(args, list):
                errors.append(f"{where}.arguments must be a list")
            else:
                for arg_index, arg in enumerate(args):
                    if not isinstance(arg, dict) or not _is_enum(arg.get("kind"), {"variable", "constant"}) or not _is_nonempty_string(arg.get("id")):
                        errors.append(f"{where}.arguments[{arg_index}] must have kind variable|constant and a non-empty id")
                    elif arg["kind"] == "variable" and not _is_variable_id(arg["id"]):
                        errors.append(f"{where}.arguments[{arg_index}].id must be a variable ID like '?x'")
                    elif arg["kind"] == "constant" and arg["id"].startswith("?"):
                        errors.append(f"{where}.arguments[{arg_index}].id must not use the variable prefix '?'")
        elif isinstance(kind, str) and kind in {"and", "or"}:
            children = node.get("children")
            if not isinstance(children, list) or len(children) < 2 or any(not _is_nonempty_string(x) for x in children):
                errors.append(f"{where}.children must contain at least two node ids")
        elif kind == "not":
            if not _is_nonempty_string(node.get("child")):
                errors.append(f"{where}.child must be a node id")
        elif isinstance(kind, str) and kind in {"forall", "exists"}:
            binder = node.get("binder")
            if not isinstance(binder, dict) or binder.get("kind") != "variable" or not _is_nonempty_string(binder.get("id")):
                errors.append(f"{where}.binder must be a variable term")
            elif not _is_variable_id(binder["id"]):
                errors.append(f"{where}.binder.id must be a variable ID like '?x'")
            if not _is_nonempty_string(node.get("child")):
                errors.append(f"{where}.child must be a node id")
        elif kind == "implies":
            if not _is_nonempty_string(node.get("antecedent")) or not _is_nonempty_string(node.get("consequent")):
                errors.append(f"{where} requires antecedent and consequent node ids")
        elif kind == "unknown" and not _is_nonempty_string(node.get("reason")):
            errors.append(f"{where}.reason must explain the unresolved structure")

    def references(node: dict[str, Any]) -> list[str]:
        kind = node.get("kind")
        if not isinstance(kind, str):
            return []
        if kind in {"and", "or"} and isinstance(node.get("children"), list):
            return [x for x in node["children"] if isinstance(x, str)]
        if kind in {"not", "forall", "exists"} and isinstance(node.get("child"), str):
            return [node["child"]]
        if kind == "implies":
            return [x for x in (node.get("antecedent"), node.get("consequent")) if isinstance(x, str)]
        return []

    for node_id, node in nodes.items():
        for child_id in references(node):
            if child_id not in nodes:
                errors.append(f"AST node {node_id} references missing child {child_id}")
    roots = analysis.get("root_node_ids")
    if not isinstance(roots, list) or any(not _is_nonempty_string(x) for x in roots):
        errors.append("analysis.root_node_ids must be a list of node ids")
    elif not roots and (nodes or analysis.get("status") == "annotated"):
        errors.append("analysis.root_node_ids must not be empty when nodes exist or analysis is annotated")
    else:
        for root_id in roots:
            if root_id not in nodes:
                errors.append(f"analysis.root_node_ids references missing node {root_id}")

    # AST references must form a DAG. The DFS also tolerates already-reported dangling refs.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            errors.append(f"AST contains a cycle through node {node_id}")
            return
        if node_id in visited or node_id not in nodes:
            return
        visiting.add(node_id)
        for child_id in references(nodes[node_id]):
            visit(child_id)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in nodes:
        visit(node_id)

    # Quantifier binding is lexical. Free variables remain valid open-formula
    # parameters; this structural pass does not infer whether a human omitted
    # an intended binder. A shared DAG node must, however, have one meaning
    # within each root: reusing it under different binder environments would
    # make its variable occurrences context-dependent.
    valid_roots = roots if isinstance(roots, list) else []
    for root_id in valid_roots:
        if not isinstance(root_id, str) or root_id not in nodes:
            continue
        stack: list[tuple[str, frozenset[str]]] = [(root_id, frozenset())]
        seen_contexts: dict[str, frozenset[str]] = {}
        while stack:
            node_id, bound = stack.pop()
            node = nodes.get(node_id)
            if node is None:
                continue
            previous_bound = seen_contexts.get(node_id)
            if previous_bound is not None:
                if previous_bound != bound:
                    errors.append(
                        f"AST node {node_id} is shared under different quantifier scopes from root {root_id}"
                    )
                continue
            seen_contexts[node_id] = bound
            kind = node.get("kind")
            child_bound = bound
            if isinstance(kind, str) and kind in {"forall", "exists"}:
                binder = node.get("binder")
                binder_id = binder.get("id") if isinstance(binder, dict) else None
                if _is_variable_id(binder_id):
                    if binder_id in bound:
                        errors.append(
                            f"AST quantifier {node_id} shadows an enclosing binder {binder_id!r}; alpha-rename binders"
                        )
                    child_bound = bound | {binder_id}
            for child_id in references(node):
                stack.append((child_id, child_bound))

    claims = analysis.get("rule_claims")
    if not isinstance(claims, list):
        errors.append("analysis.rule_claims must be a list")
        claims = []
    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        where = f"analysis.rule_claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{where} must be an object")
            continue
        claim_id = claim.get("id")
        if not _is_nonempty_string(claim_id):
            errors.append(f"{where}.id must be a non-empty string")
        elif claim_id in claim_ids:
            errors.append(f"duplicate rule claim id: {claim_id}")
        else:
            claim_ids.add(claim_id)
        if not _is_enum(claim.get("relation"), CLAIM_RELATIONS):
            errors.append(f"{where}.relation must be one of {sorted(CLAIM_RELATIONS)}")
        if not _is_enum(claim.get("direction"), CLAIM_DIRECTIONS):
            errors.append(f"{where}.direction must be one of {sorted(CLAIM_DIRECTIONS)}")
        if not _is_enum(claim.get("confidence"), CONFIDENCE_VALUES):
            errors.append(f"{where}.confidence must be one of {sorted(CONFIDENCE_VALUES)}")
        if not _is_enum(claim.get("semantic_support"), SEMANTIC_SUPPORT_VALUES):
            errors.append(f"{where}.semantic_support must be one of {sorted(SEMANTIC_SUPPORT_VALUES)}")
        if schema_version in {"0.4-draft", "0.5-draft", "0.6-draft", "0.7-draft"}:
            inference_basis = claim.get("inference_basis")
            if (not isinstance(inference_basis, list) or not inference_basis
                    or any(not _is_enum(value, INFERENCE_BASIS_VALUES) for value in inference_basis)):
                errors.append(f"{where}.inference_basis must be a non-empty list containing only {sorted(INFERENCE_BASIS_VALUES)}")
            else:
                if len(inference_basis) != len(set(inference_basis)):
                    errors.append(f"{where}.inference_basis must not contain duplicates")
                if "unclear" in inference_basis and len(inference_basis) != 1:
                    errors.append(f"{where}.inference_basis='unclear' must be the only value when present")
                if "unassessed" in inference_basis and len(inference_basis) != 1:
                    errors.append(f"{where}.inference_basis='unassessed' must be the only value when present")
                if (claim.get("semantic_support") == "unassessed"
                        and inference_basis != ["unassessed"]):
                    errors.append(f"{where}.inference_basis must be ['unassessed'] when semantic_support is unassessed")
                if (claim.get("semantic_support") != "unassessed"
                        and "unassessed" in inference_basis):
                    errors.append(f"{where}.inference_basis cannot be unassessed when semantic_support has been assessed")
        if "support_reasons" in claim:
            support_reasons = claim.get("support_reasons")
            if not isinstance(support_reasons, list):
                errors.append(f"{where}.support_reasons must be a list when supplied")
            else:
                if (schema_version in {"0.3-draft", "0.4-draft", "0.5-draft", "0.6-draft", "0.7-draft"}
                        and claim.get("semantic_support") in {"not_supported", "uncertain"}
                        and not support_reasons):
                    errors.append(f"{where}.support_reasons must be non-empty for schema {schema_version} {claim['semantic_support']} claims")
                invalid_reasons = [reason for reason in support_reasons
                                   if not _is_enum(reason, SUPPORT_REASON_VALUES)]
                if invalid_reasons:
                    errors.append(
                        f"{where}.support_reasons contains values outside {sorted(SUPPORT_REASON_VALUES)}"
                    )
                if not invalid_reasons and len(support_reasons) != len(set(support_reasons)):
                    errors.append(f"{where}.support_reasons must not contain duplicates")
                support_status = claim.get("semantic_support")
                allowed_reasons = ({
                    "not_supported": NOT_SUPPORTED_REASON_VALUES,
                    "uncertain": UNCERTAIN_REASON_VALUES,
                    "supported": set(),
                    "unassessed": set(),
                }.get(support_status) if isinstance(support_status, str) else None)
                if (allowed_reasons is not None and not invalid_reasons
                        and any(reason not in allowed_reasons for reason in support_reasons)):
                    errors.append(f"{where}.support_reasons are incompatible with semantic_support={support_status!r}")
        elif (schema_version in {"0.3-draft", "0.4-draft", "0.5-draft", "0.6-draft", "0.7-draft"}
              and claim.get("semantic_support") in ("not_supported", "uncertain")):
            errors.append(f"{where}.support_reasons is required for schema {schema_version} {claim['semantic_support']} claims")
        formula_id = claim.get("formula_node_id")
        if not _is_nonempty_string(formula_id) or formula_id not in nodes:
            errors.append(f"{where}.formula_node_id must reference an existing AST node")
        if schema_version != "0.7-draft" and "target_variable" in claim:
            errors.append(f"{where}.target_variable requires schema_version='0.7-draft'")
        if schema_version in {"0.5-draft", "0.6-draft", "0.7-draft"}:
            if schema_version == "0.5-draft" and "variable_sort_judgments" in claim:
                errors.append(f"{where}.variable_sort_judgments requires schema_version='0.6-draft'")
            if schema_version in {"0.6-draft", "0.7-draft"} and "variable_sorts" in claim:
                errors.append(f"{where}.variable_sorts is superseded by variable_sort_judgments in schema {schema_version}")
            formula_variables: set[str] = set()
            if isinstance(formula_id, str) and formula_id in nodes:
                pending_variables = [formula_id]
                visited_formula_nodes: set[str] = set()
                while pending_variables:
                    current_id = pending_variables.pop()
                    if current_id in visited_formula_nodes:
                        continue
                    visited_formula_nodes.add(current_id)
                    current_node = nodes.get(current_id)
                    if not isinstance(current_node, dict):
                        continue
                    for argument in current_node.get("arguments", []):
                        if (isinstance(argument, dict) and argument.get("kind") == "variable"
                                and _is_variable_id(argument.get("id"))):
                            formula_variables.add(argument["id"])
                        if (schema_version == "0.7-draft" and isinstance(argument, dict)
                                and argument.get("kind") == "constant"
                                and isinstance(argument.get("id"), str)
                                and argument["id"].startswith("?")):
                            errors.append(
                                f"{where}.formula constants cannot start with '?' in schema 0.7-draft"
                            )
                    binder = current_node.get("binder")
                    if (isinstance(binder, dict) and binder.get("kind") == "variable"
                            and _is_variable_id(binder.get("id"))):
                        formula_variables.add(binder["id"])
                    pending_variables.extend(references(current_node))
            if schema_version == "0.5-draft":
                variable_sorts = claim.get("variable_sorts")
                if not isinstance(variable_sorts, dict):
                    errors.append(f"{where}.variable_sorts must map formula variable IDs to non-empty sort names")
                    variable_sorts = {}
                for variable, sort in variable_sorts.items():
                    if not _is_variable_id(variable) or not _is_nonempty_string(sort):
                        errors.append(f"{where}.variable_sorts must map '?variable' IDs to non-empty sort names")
                declared_variables = set(variable_sorts)
            else:
                judgments = claim.get("variable_sort_judgments")
                if not isinstance(judgments, dict):
                    errors.append(f"{where}.variable_sort_judgments must map formula variable IDs to judgment objects")
                    judgments = {}
                for variable, judgment in judgments.items():
                    judgment_where = f"{where}.variable_sort_judgments[{variable!r}]"
                    if not _is_variable_id(variable):
                        errors.append(f"{where}.variable_sort_judgments keys must be '?variable' IDs")
                    if not isinstance(judgment, dict):
                        errors.append(f"{judgment_where} must be an object")
                        continue
                    status = judgment.get("status")
                    sort = judgment.get("sort")
                    basis = judgment.get("basis")
                    if not _is_enum(status, {"assigned", "unresolved"}):
                        errors.append(f"{judgment_where}.status must be 'assigned' or 'unresolved'")
                    if status == "assigned" and not _is_nonempty_string(sort):
                        errors.append(f"{judgment_where}.sort must be non-empty when status is assigned")
                    if status == "unresolved" and sort is not None:
                        errors.append(f"{judgment_where}.sort must be null when status is unresolved")
                    if not _is_enum(basis, VARIABLE_SORT_BASES):
                        errors.append(f"{judgment_where}.basis must be one of {sorted(VARIABLE_SORT_BASES)}")
                    elif status == "unresolved" and basis != "unknown":
                        errors.append(f"{judgment_where}.basis must be 'unknown' when status is unresolved")
                    elif status == "assigned" and basis == "unknown":
                        errors.append(f"{judgment_where}.basis cannot be 'unknown' when status is assigned")
                    rationale = judgment.get("rationale")
                    if not _is_nonempty_string(rationale):
                        errors.append(f"{judgment_where}.rationale must be a non-empty string")
                    spans = judgment.get("evidence_spans")
                    if not isinstance(spans, list):
                        errors.append(f"{judgment_where}.evidence_spans must be a list")
                    else:
                        for span_index, span in enumerate(spans):
                            _check_span(span, gloss, f"{judgment_where}.evidence_spans[{span_index}]", errors)
                        if basis == "gloss_span" and not spans:
                            errors.append(f"{judgment_where}.evidence_spans must be non-empty for basis='gloss_span'")
                    if status == "unresolved" and spans:
                        errors.append(f"{judgment_where}.evidence_spans must be empty when status is unresolved")
                declared_variables = set(judgments)
            if schema_version == "0.7-draft":
                target_variable = claim.get("target_variable")
                if not _is_variable_id(target_variable):
                    errors.append(f"{where}.target_variable must be a variable ID like '?x'")
                elif isinstance(formula_id, str) and formula_id in nodes:
                    free_variables: set[str] = set()
                    binder_variables: set[str] = set()
                    pending_scopes = [(formula_id, frozenset())]
                    seen_scopes: set[tuple[str, frozenset[str]]] = set()
                    while pending_scopes:
                        current_id, bound = pending_scopes.pop()
                        scope_key = (current_id, bound)
                        if scope_key in seen_scopes:
                            continue
                        seen_scopes.add(scope_key)
                        current_node = nodes.get(current_id)
                        if not isinstance(current_node, dict):
                            continue
                        if current_node.get("kind") == "atom":
                            for argument in current_node.get("arguments", []):
                                variable = argument.get("id") if isinstance(argument, dict) else None
                                if (isinstance(argument, dict) and argument.get("kind") == "variable"
                                        and _is_variable_id(variable) and variable not in bound):
                                    free_variables.add(variable)
                        next_bound = bound
                        if current_node.get("kind") in {"forall", "exists"}:
                            binder = current_node.get("binder")
                            binder_id = binder.get("id") if isinstance(binder, dict) else None
                            if _is_variable_id(binder_id):
                                binder_variables.add(binder_id)
                                next_bound = bound | {binder_id}
                        pending_scopes.extend((child_id, next_bound) for child_id in references(current_node))
                    if target_variable not in free_variables:
                        errors.append(f"{where}.target_variable must occur free in an atom of its formula")
                    if target_variable in binder_variables:
                        errors.append(f"{where}.target_variable must not also be used as a quantifier binder; alpha-rename the binder")
            if formula_variables - declared_variables:
                map_label = "variable_sorts" if schema_version == "0.5-draft" else "variable sort judgments"
                errors.append(
                    f"{where}.{map_label} is missing variables {sorted(formula_variables - declared_variables)}"
                )
            if declared_variables - formula_variables:
                map_label = "variable_sorts" if schema_version == "0.5-draft" else "variable sort judgments"
                errors.append(
                    f"{where}.{map_label} declares unused variables {sorted(declared_variables - formula_variables)}"
                )
        evidence = claim.get("evidence_spans")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{where}.evidence_spans must contain at least one source span")
        else:
            for span_index, span in enumerate(evidence):
                _check_span(span, gloss, f"{where}.evidence_spans[{span_index}]", errors)
            evidence_bounds = [
                bounds for span in evidence
                if (bounds := _valid_span_bounds(span, len(gloss))) is not None
            ]
            formula_subtree_ids: set[str] = set()
            pending = [formula_id] if isinstance(formula_id, str) and formula_id in nodes else []
            while pending:
                node_id = pending.pop()
                if node_id in formula_subtree_ids:
                    continue
                formula_subtree_ids.add(node_id)
                current = nodes.get(node_id)
                if current is None:
                    continue
                # Dangling child references are reported as structural errors
                # elsewhere; skip them here instead of raising KeyError.
                pending.extend(ref for ref in references(current) if ref in nodes)
            uncovered_node_ids = []
            for node_id in sorted(formula_subtree_ids):
                node_bounds = _valid_span_bounds(nodes[node_id].get("span"), len(gloss))
                if (node_bounds is not None and evidence_bounds
                        and not _span_covered_by_union(node_bounds, evidence_bounds)):
                    uncovered_node_ids.append(node_id)
            if uncovered_node_ids:
                errors.append(
                    f"{where}.evidence_spans must fully cover every formula-subtree node span; "
                    f"uncovered node IDs: {uncovered_node_ids}"
                )
        if "nli_hypothesis" in claim or "nli_hypothesis_sha256" in claim:
            hypothesis = claim.get("nli_hypothesis")
            hypothesis_hash = claim.get("nli_hypothesis_sha256")
            if not _is_nonempty_string(hypothesis):
                errors.append(f"{where}.nli_hypothesis must be a non-empty string when supplied")
            if not isinstance(hypothesis_hash, str) or not SHA256_RE.fullmatch(hypothesis_hash):
                errors.append(f"{where}.nli_hypothesis_sha256 must be a 64-character hexadecimal SHA-256")
            elif isinstance(hypothesis, str) and hashlib.sha256(hypothesis.encode("utf-8")).hexdigest() != hypothesis_hash.lower():
                errors.append(f"{where}.nli_hypothesis_sha256 does not match UTF-8 SHA-256 of nli_hypothesis")

    projection = analysis.get("horn_projection")
    if not isinstance(projection, dict):
        errors.append("analysis.horn_projection must be an object")
    else:
        if not _is_enum(projection.get("status"), PROJECTION_STATUSES):
            errors.append(f"analysis.horn_projection.status must be one of {sorted(PROJECTION_STATUSES)}")
        for key in ("rule_ids", "omissions"):
            value = projection.get(key)
            if not isinstance(value, list) or any(not _is_nonempty_string(x) for x in value):
                errors.append(f"analysis.horn_projection.{key} must be a list of non-empty strings")

    annotation = record.get("annotation")
    if not isinstance(annotation, dict):
        errors.append("annotation must be an object")
    else:
        if not _is_nonempty_string(annotation.get("annotator_id")):
            errors.append("annotation.annotator_id must be a non-empty pseudonymous id")
        if not _is_enum(annotation.get("adjudication_status"), ADJUDICATION_STATUSES):
            errors.append(f"annotation.adjudication_status must be one of {sorted(ADJUDICATION_STATUSES)}")
        if not isinstance(annotation.get("notes"), list) or any(not isinstance(x, str) for x in annotation["notes"]):
            errors.append("annotation.notes must be a list of strings")
    if not _is_enum(record.get("split"), SPLIT_VALUES):
        errors.append(f"split must be one of {sorted(SPLIT_VALUES)}")
    return errors


def validate_dataset(records: list[dict[str, Any]], line_numbers: list[int] | None = None) -> list[str]:
    """Check uniqueness and prevent lemma/synset leakage across data splits."""
    errors: list[str] = []
    annotation_ids: set[str] = set()
    lemma_splits: dict[str, str] = {}
    synset_splits: dict[str, str] = {}
    if line_numbers is not None and len(line_numbers) != len(records):
        raise ValueError("line_numbers must align one-to-one with records")
    for index, record in enumerate(records, start=1):
        line_number = line_numbers[index - 1] if line_numbers is not None else index
        for error in validate_record(record):
            errors.append(f"line {line_number}: {error}")
        annotation_id = record.get("annotation_id") if isinstance(record, dict) else None
        if isinstance(annotation_id, str):
            if annotation_id in annotation_ids:
                errors.append(f"line {line_number}: duplicate annotation_id {annotation_id}")
            annotation_ids.add(annotation_id)
        if not isinstance(record, dict):
            continue
        split = record.get("split")
        sense = record.get("sense")
        if not isinstance(sense, dict) or not _is_enum(split, SPLIT_VALUES) or split == "unassigned":
            continue
        synset_id = sense.get("synset_id")
        if isinstance(synset_id, str):
            previous = synset_splits.setdefault(synset_id, split)
            if previous != split:
                errors.append(f"line {line_number}: synset {synset_id} appears in both {previous} and {split}")
        lemmas = sense.get("lemmas")
        if isinstance(lemmas, list):
            for lemma in lemmas:
                if not isinstance(lemma, str):
                    continue
                previous = lemma_splits.setdefault(lemma.casefold(), split)
                if previous != split:
                    errors.append(f"line {line_number}: lemma {lemma!r} appears in both {previous} and {split}")
    return errors


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[int], list[str]]:
    records: list[dict[str, Any]] = []
    line_numbers: list[int] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_number}: record must be a JSON object")
                continue
            records.append(record)
            line_numbers.append(line_number)
    return records, line_numbers, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="annotation JSONL to validate")
    args = parser.parse_args(argv)
    try:
        records, line_numbers, errors = load_jsonl(args.jsonl)
    except OSError as exc:
        print(f"cannot read {args.jsonl}: {exc}", file=sys.stderr)
        return 2
    errors.extend(validate_dataset(records, line_numbers))
    if errors:
        print("Annotation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Valid annotation JSONL: {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
