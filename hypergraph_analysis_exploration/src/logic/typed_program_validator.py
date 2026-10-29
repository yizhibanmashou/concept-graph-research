"""Validate Datalog programs against an explicit, versioned sort signature.

This checks formal type compatibility only. It does not establish that a
predicate signature or a source annotation is linguistically correct.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


TYPE_SYSTEM_SCHEMA_VERSION = "datalog-type-system/1"
TYPE_SYSTEM_FIELDS = {
    "schema_version", "type_system_id", "version", "sorts",
    "predicate_signatures", "constant_sorts", "rule_variable_sorts",
}


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _name(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sort_graph(type_system: Any) -> tuple[dict[str, list[str]], list[str]]:
    errors: list[str] = []
    if not isinstance(type_system, dict):
        return {}, ["type_system must be an object"]
    extra = set(type_system) - TYPE_SYSTEM_FIELDS
    if extra:
        errors.append(f"type_system has unsupported field(s): {sorted(extra)}")
    if type_system.get("schema_version") != TYPE_SYSTEM_SCHEMA_VERSION:
        errors.append(f"type_system.schema_version must be {TYPE_SYSTEM_SCHEMA_VERSION!r}")
    for field in ("type_system_id", "version"):
        if not _name(type_system.get(field)):
            errors.append(f"type_system.{field} must be a non-empty string")

    raw_sorts = type_system.get("sorts")
    parents: dict[str, list[str]] = {}
    if not isinstance(raw_sorts, dict) or not raw_sorts:
        errors.append("type_system.sorts must be a non-empty object mapping sorts to parent sorts")
        raw_sorts = {}
    for sort, sort_parents in raw_sorts.items():
        if not _name(sort):
            errors.append("type_system.sorts contains an invalid sort name")
            continue
        if (not isinstance(sort_parents, list)
                or any(not _name(parent) for parent in sort_parents)
                or len(set(sort_parents)) != len(sort_parents)):
            errors.append(f"type_system.sorts[{sort!r}] must be a duplicate-free list of parent sorts")
            continue
        parents[sort] = sort_parents
    for sort, sort_parents in parents.items():
        for parent in sort_parents:
            if parent not in parents:
                errors.append(f"unknown parent sort {parent!r} declared for {sort!r}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(sort: str) -> None:
        if sort in visiting:
            errors.append(f"cycle in sort hierarchy at {sort!r}")
            return
        if sort in visited:
            return
        visiting.add(sort)
        for parent in parents.get(sort, []):
            if parent in parents:
                visit(parent)
        visiting.remove(sort)
        visited.add(sort)

    for sort in parents:
        visit(sort)
    return parents, errors


def validate_typed_program(program: Any) -> dict[str, Any]:
    """Return a deterministic type-check report for a Datalog program.

    A program must include ``type_system`` to opt into this check. Every used
    predicate must have a signature; every used constant and rule variable must
    have declared sort(s). A declared subtype is accepted where its parent sort
    is required. Missing or malformed declarations fail closed.
    """
    errors: list[str] = []
    if not isinstance(program, dict):
        return {"valid": False, "errors": ["program must be an object"]}
    type_system = program.get("type_system")
    parents, sort_errors = _sort_graph(type_system)
    errors.extend(sort_errors)
    if not isinstance(type_system, dict):
        return {"valid": False, "errors": errors}

    raw_signatures = type_system.get("predicate_signatures")
    signatures: dict[str, list[str]] = {}
    if not isinstance(raw_signatures, dict):
        errors.append("type_system.predicate_signatures must be an object")
        raw_signatures = {}
    for predicate, signature in raw_signatures.items():
        if not _name(predicate):
            errors.append("type_system.predicate_signatures contains an invalid predicate name")
            continue
        if not isinstance(signature, list) or any(not _name(sort) for sort in signature):
            errors.append(f"signature for {predicate!r} must be a list of sort names")
            continue
        signatures[predicate] = signature
        for sort in signature:
            if sort not in parents:
                errors.append(f"signature for {predicate!r} references unknown sort {sort!r}")

    raw_constants = type_system.get("constant_sorts")
    constants: dict[str, list[str]] = {}
    if not isinstance(raw_constants, dict):
        errors.append("type_system.constant_sorts must be an object")
        raw_constants = {}
    for constant, sorts in raw_constants.items():
        if not _name(constant) or constant.startswith("?"):
            errors.append("type_system.constant_sorts contains an invalid constant")
            continue
        if (not isinstance(sorts, list) or not sorts
                or any(not _name(sort) for sort in sorts)
                or len(set(sorts)) != len(sorts)):
            errors.append(f"constant sorts for {constant!r} must be a non-empty duplicate-free list")
            continue
        constants[constant] = sorts
        for sort in sorts:
            if sort not in parents:
                errors.append(f"constant {constant!r} references unknown sort {sort!r}")

    raw_rule_variable_sorts = type_system.get("rule_variable_sorts", {})
    rule_variable_sorts: dict[str, dict[str, str]] = {}
    if not isinstance(raw_rule_variable_sorts, dict):
        errors.append("type_system.rule_variable_sorts must be an object when supplied")
        raw_rule_variable_sorts = {}
    for rule_id, declarations in raw_rule_variable_sorts.items():
        if not _name(rule_id) or not isinstance(declarations, dict):
            errors.append("type_system.rule_variable_sorts must map rule IDs to variable-sort objects")
            continue
        parsed: dict[str, str] = {}
        for variable, sort in declarations.items():
            if (not isinstance(variable, str) or not variable.startswith("?") or len(variable) < 2
                    or not _name(sort)):
                errors.append(f"type_system.rule_variable_sorts[{rule_id!r}] has an invalid declaration")
                continue
            parsed[variable] = sort
            if sort not in parents:
                errors.append(f"rule {rule_id!r} variable {variable!r} references unknown sort {sort!r}")
        rule_variable_sorts[rule_id] = parsed

    # is_subsort(child, parent) includes equality and transitive ancestry.
    def is_subsort(child: str, required: str) -> bool:
        pending = [child]
        seen: set[str] = set()
        while pending:
            current = pending.pop()
            if current == required:
                return True
            if current in seen:
                continue
            seen.add(current)
            pending.extend(parents.get(current, []))
        return False

    raw_facts = program.get("facts", [])
    raw_rules = program.get("rules", [])
    query = program.get("query")
    atoms: list[tuple[str, Any, dict[str, str] | None, str]] = []
    if not isinstance(raw_facts, list):
        errors.append("facts must be a list")
        raw_facts = []
    for index, fact in enumerate(raw_facts):
        atom = fact.get("atom", fact) if isinstance(fact, dict) else None
        atoms.append((f"facts[{index}]", atom, None, "ground"))
    if not isinstance(raw_rules, list):
        errors.append("rules must be a list")
        raw_rules = []
    program_rule_ids = set()
    for index, rule in enumerate(raw_rules):
        if isinstance(rule, dict):
            rule_id = rule.get("id", str(index))
            if _name(rule_id):
                program_rule_ids.add(rule_id)
    unused_rule_type_ids = set(rule_variable_sorts) - program_rule_ids
    if unused_rule_type_ids:
        errors.append(f"type_system declares unknown rule IDs {sorted(unused_rule_type_ids)}")
    for index, rule in enumerate(raw_rules):
        if not isinstance(rule, dict):
            errors.append(f"rules[{index}] must be an object")
            continue
        raw_rule_id = rule.get("id", str(index))
        valid_rule_id = _name(raw_rule_id)
        rule_id = raw_rule_id if valid_rule_id else f"<invalid-rule-{index}>"
        if not valid_rule_id:
            errors.append(f"rules[{index}].id must be a non-empty string")
        label = f"rule {rule_id!r}"
        variable_sorts = rule.get("variable_sorts")
        if variable_sorts is not None and rule_id in rule_variable_sorts:
            errors.append(f"{label} declares variable sorts both inline and in type_system")
        if variable_sorts is None:
            variable_sorts = rule_variable_sorts.get(rule_id)
        if not isinstance(variable_sorts, dict) or any(
            not isinstance(var, str) or not var.startswith("?") or len(var) < 2
            or not _name(sort) for var, sort in (variable_sorts.items() if isinstance(variable_sorts, dict) else [])
        ):
            errors.append(f"{label}.variable_sorts must map '?variable' names to sort names")
            variable_sorts = {}
        for variable, sort in variable_sorts.items():
            if sort not in parents:
                errors.append(f"{label} variable {variable!r} references unknown sort {sort!r}")
        atoms.append((f"{label}.head", rule.get("head"), variable_sorts, "rule"))
        body = rule.get("body")
        if not isinstance(body, list):
            errors.append(f"{label}.body must be a list")
            body = []
        for body_index, atom in enumerate(body):
            atoms.append((f"{label}.body[{body_index}]", atom, variable_sorts, "rule"))
    atoms.append(("query", query, None, "ground"))

    for label, atom, variable_sorts, atom_kind in atoms:
        if not isinstance(atom, dict):
            errors.append(f"{label} must be an atom object")
            continue
        predicate = atom.get("predicate")
        arguments = atom.get("arguments", [])
        if not _name(predicate) or not isinstance(arguments, list):
            errors.append(f"{label} must contain a predicate and argument list")
            continue
        signature = signatures.get(predicate)
        if signature is None:
            errors.append(f"{label} uses predicate {predicate!r} without a declared signature")
            continue
        if len(arguments) != len(signature):
            errors.append(
                f"{label} predicate {predicate!r} has arity {len(arguments)}, expected {len(signature)}"
            )
            continue
        for position, (term, required_sort) in enumerate(zip(arguments, signature)):
            where = f"{label} argument {position + 1}"
            if not isinstance(term, str) or not term:
                errors.append(f"{where} must be a non-empty string")
                continue
            if term.startswith("?"):
                if atom_kind != "rule":
                    errors.append(f"{where} is variable {term!r} in a ground atom")
                    continue
                actual_sort = variable_sorts.get(term) if isinstance(variable_sorts, dict) else None
                if actual_sort is None:
                    errors.append(f"{label} variable {term!r} has no declared sort")
                elif actual_sort in parents and required_sort in parents and not is_subsort(actual_sort, required_sort):
                    errors.append(
                        f"{where} variable {term!r} has sort {actual_sort!r}, incompatible with {required_sort!r}"
                    )
            else:
                actual_sorts = constants.get(term)
                if actual_sorts is None:
                    errors.append(f"{where} constant {term!r} has no declared sort")
                elif (required_sort in parents
                      and not any(sort in parents and is_subsort(sort, required_sort) for sort in actual_sorts)):
                    errors.append(
                        f"{where} constant {term!r} has sorts {actual_sorts!r}, incompatible with {required_sort!r}"
                    )
    for index, rule in enumerate(raw_rules):
        if not isinstance(rule, dict):
            continue
        raw_rule_id = rule.get("id", str(index))
        rule_id = raw_rule_id if _name(raw_rule_id) else f"<invalid-rule-{index}>"
        variable_sorts = rule.get("variable_sorts")
        if variable_sorts is None:
            variable_sorts = rule_variable_sorts.get(rule_id)
        if not isinstance(variable_sorts, dict):
            continue
        declared = set(variable_sorts)
        used: set[str] = set()
        rule_atoms = [rule.get("head")]
        body = rule.get("body")
        if isinstance(body, list):
            rule_atoms.extend(body)
        for atom in rule_atoms:
            if not isinstance(atom, dict) or not isinstance(atom.get("arguments", []), list):
                continue
            used.update(term for term in atom.get("arguments", [])
                        if isinstance(term, str) and term.startswith("?"))
        missing = used - declared
        unused = declared - used
        if missing:
            errors.append(f"rule {rule_id!r} missing sorts for variables {sorted(missing)}")
        if unused:
            errors.append(f"rule {rule_id!r} declares unused variables {sorted(unused)}")

    try:
        signature_hash = _sha256_json(type_system)
    except (TypeError, ValueError):
        signature_hash = None
        errors.append("type_system must contain finite JSON-compatible values")
    return {
        "valid": not errors,
        "type_system_id": type_system.get("type_system_id"),
        "type_system_version": type_system.get("version"),
        "schema_version": type_system.get("schema_version"),
        "signature_table_sha256": signature_hash,
        "sort_count": len(parents),
        "predicate_signature_count": len(signatures),
        "constant_count": len(constants),
        "errors": errors,
        "interpretation_limit": (
            "Type validity is relative to the declared signature table. This report does not establish that "
            "the ontology/signatures are correct or that source text entails any rule."
        ),
    }
