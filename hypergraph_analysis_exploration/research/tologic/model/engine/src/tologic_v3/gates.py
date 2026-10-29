"""Fail-closed local checks and capture-avoiding expansion for V3.

Passing these checks certifies syntax, provenance and call discipline only.  It
does not certify that an inventory is exhaustive or that a formula is faithful.
Those decisions belong to independent reviewers and the publication controller.
"""
from __future__ import annotations

from copy import deepcopy
from functools import wraps
import re
from typing import Any

from .common import canonical_hash, provider_key
from .parameter_projection import prepare_parameter_projection
from .nominalization import RESERVED as _NOMINALIZATION_INTERNAL_SYMBOLS


_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_BASE_TYPES = {"E", "V", "Time", "World", "Prop"}
_STRUCTURES = {"Agent", "Theme", "Happen", "ImplicitSubj", "World"}


def _fail_closed(function):
    """Model-produced malformed JSON must never escape as an accepted result."""
    @wraps(function)
    def guarded(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (TypeError, ValueError, KeyError, IndexError, AttributeError, RecursionError) as exc:
            return [{"code": "MALFORMED_VALIDATION_INPUT", "path": function.__name__,
                     "message": f"Input cannot be safely interpreted ({type(exc).__name__}); no acceptance was issued."}]
    return guarded


def _issue(out: list, code: str, path: str, message: str) -> None:
    out.append({"code": code, "path": path, "message": message})


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _type(value: Any) -> bool:
    if isinstance(value, str):
        return value in _BASE_TYPES
    return (isinstance(value, dict) and set(value) == {"arrow"}
            and isinstance(value["arrow"], list) and len(value["arrow"]) >= 2
            and all(_type(x) for x in value["arrow"]))


def _matches(actual: Any, expected: Any) -> bool:
    # A list denotes explicitly allowed alternatives, never a coercion.
    return actual in expected if isinstance(expected, list) else actual == expected


def _parameters(values: Any, out: list, path: str, *, allow_empty: bool = False) -> dict:
    result = {}
    if not isinstance(values, list) or (not values and not allow_empty):
        _issue(out, "INVALID_PARAMETERS", path, "An ordered parameter list is required; local binders must be nonempty.")
        return result
    for i, value in enumerate(values):
        here = f"{path}[{i}]"
        if not isinstance(value, dict):
            _issue(out, "INVALID_PARAMETER", here, "Parameter must be an object.")
            continue
        if set(value) - {"name", "type", "role"} or ("role" in value and not _text(value["role"])):
            _issue(out, "INVALID_PARAMETER", here, "Parameters contain only name, type and optional textual role.")
        name = value.get("name")
        if not isinstance(name, str) or not _NAME.fullmatch(name):
            _issue(out, "INVALID_PARAMETER", here, "Invalid variable name.")
            continue
        if name in result:
            _issue(out, "DUPLICATE_PARAMETER", here, f"Duplicate variable {name}.")
        if not _type(value.get("type")):
            _issue(out, "INVALID_TYPE", here, "Unknown or malformed type.")
        result[name] = value.get("type")
    return result


def _occurrences(source: dict) -> dict:
    rows = source.get("occurrences", []) if isinstance(source, dict) else []
    rows = rows if isinstance(rows, list) else []
    return {x.get("occurrence_id"): x for x in rows
            if isinstance(x, dict) and isinstance(x.get("occurrence_id"), str)}


def _basis(source: dict, context: dict) -> bool:
    return source.get("synset_id") in context.get("basis_ids", [])


def _plan_term(value):
    if isinstance(value, str):
        return {"var": value}
    if isinstance(value, dict) and set(value) == {"implicit_subject"} and isinstance(value["implicit_subject"], str):
        return {"op": "struct", "name": "ImplicitSubj", "args": [{"var": value["implicit_subject"]}]}
    if isinstance(value, dict) and set(value) == {"world_of"} and isinstance(value["world_of"], str):
        return {"op": "struct", "name": "World", "args": [{"var": value["world_of"]}]}
    raise ValueError("Invalid binding-plan term")


def _plan_atom(row):
    return {"op": "struct", "name": row["name"], "args": [_plan_term(x) for x in row["arguments"]]}


def _binding_scopes(plan, global_environment, out, path):
    """Resolve explicitly certified lambda/forall locals without globalizing them."""
    raw = plan.get("scopes", [])
    if not isinstance(raw, list):
        _issue(out, "INVALID_BINDING_SCOPES", path, "Binding scopes must be a list.")
        return {}, {}
    specs = {}
    for row in raw:
        if (not isinstance(row, dict) or set(row) != {"scope_id", "parent_scope", "kind", "variables"}
                or not _text(row.get("scope_id")) or row.get("kind") not in ("lambda", "forall")
                or (row.get("parent_scope") is not None and not _text(row.get("parent_scope")))):
            _issue(out, "INVALID_BINDING_SCOPE", path, "Scope requires identity, parent, lambda/forall kind and typed local variables.")
            continue
        sid = row["scope_id"]
        if sid in specs:
            _issue(out, "DUPLICATE_BINDING_SCOPE", path, "A local scope identity can be declared only once.")
        specs[sid] = row
    environments = {}
    pending = dict(specs)
    while pending:
        progressed = False
        for sid, row in list(pending.items()):
            parent = row["parent_scope"]
            if parent is not None and parent not in environments:
                continue
            inherited = dict(global_environment if parent is None else environments[parent])
            local = _parameters(row["variables"], out, f"{path}.{sid}.variables")
            if set(local) & set(inherited):
                _issue(out, "BINDING_SCOPE_CAPTURE", path, "Local scope variables cannot shadow external inputs, witnesses or ancestor locals.")
            environments[sid] = {**inherited, **local}
            del pending[sid]
            progressed = True
        if not progressed:
            _issue(out, "INVALID_BINDING_SCOPE_PARENT", path, "Scope parents must exist and form an acyclic hierarchy.")
            break
    return specs, environments


def _walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _free(node: Any, bound: frozenset = frozenset()) -> set:
    if not isinstance(node, dict):
        return set()
    if set(node) == {"var"}:
        return {node["var"]} - bound if isinstance(node["var"], str) else set()
    if node.get("op") in ("exists", "forall", "lambda"):
        key = "parameters" if node["op"] == "lambda" else "variables"
        parameters = node.get(key, [])
        parameters = parameters if isinstance(parameters, list) else []
        local = {v["name"] for v in parameters if isinstance(v, dict) and isinstance(v.get("name"), str)}
        return _free(node.get("body"), bound | local)
    result = set()
    for value in node.values():
        if isinstance(value, dict):
            result |= _free(value, bound)
        elif isinstance(value, list):
            for item in value:
                result |= _free(item, bound)
    return result


@_fail_closed
def validate_source(source: dict, context: dict) -> list:
    out = []
    if not isinstance(source, dict):
        return [{"code": "INVALID_SOURCE", "path": "source", "message": "Source must be an object."}]
    if source.get("schema_version") != "v3.source/1":
        _issue(out, "INVALID_SOURCE_SCHEMA", "source.schema_version", "Expected v3.source/1.")
    if not _text(source.get("synset_id")):
        _issue(out, "INVALID_SOURCE_ID", "source.synset_id", "A fixed synset identity is required.")
    if not _text(source.get("definition")):
        _issue(out, "INVALID_DEFINITION", "source.definition", "Original definition is required.")
    if type(source.get("is_basis")) is not bool or source.get("is_basis") != _basis(source, context):
        _issue(out, "BASIS_MEMBERSHIP_MISMATCH", "source.is_basis", "Basis membership is controller-owned.")
    if source.get("blocking_issues"):
        _issue(out, "SOURCE_BLOCKED", "source.blocking_issues", "Imported source has unresolved alignment or identity issues.")
    rows = source.get("occurrences")
    if not isinstance(rows, list):
        _issue(out, "INVALID_OCCURRENCES", "source.occurrences", "Fixed WSD occurrence records are required.")
        return out
    seen = set()
    definition = source.get("definition", "")
    if not isinstance(definition, str):
        definition = ""
    for i, row in enumerate(rows):
        path = f"source.occurrences[{i}]"
        if not isinstance(row, dict):
            _issue(out, "INVALID_OCCURRENCE", path, "Occurrence must be an object.")
            continue
        occurrence = row.get("occurrence_id")
        if not _text(occurrence) or (isinstance(occurrence, str) and occurrence in seen):
            _issue(out, "INVALID_OCCURRENCE_ID", path, "Occurrence identity is missing or duplicated.")
        if isinstance(occurrence, str):
            seen.add(occurrence)
        if not _text(row.get("synset_id")):
            _issue(out, "MISSING_FIXED_WSD", path, "An already resolved synset is required.")
        start, end = row.get("start"), row.get("end")
        valid_span = (type(start) is int and type(end) is int
                      and 0 <= start < end <= len(definition))
        if not valid_span or definition[start:end] != row.get("text"):
            _issue(out, "OCCURRENCE_SPAN_MISMATCH", path, "Occurrence must match the exact original definition span.")
    return out


@_fail_closed
def validate_inventory(source: dict, inventory: dict, context: dict) -> list:
    out = validate_source(source, context)
    if not isinstance(source, dict):
        return out
    if not isinstance(inventory, dict):
        _issue(out, "INVALID_INVENTORY", "inventory", "Inventory must be an object.")
        return out
    if inventory.get("synset_id") != source.get("synset_id"):
        _issue(out, "INVENTORY_SOURCE_MISMATCH", "inventory.synset_id", "Inventory cannot replace the source identity.")
    coverage = inventory.get("coverage", {})
    if (not isinstance(coverage, dict) or coverage.get("complete") is not True
            or not _text(coverage.get("rationale")) or not isinstance(coverage.get("evidence_ids"), list)):
        _issue(out, "INCOMPLETE_USAGE_INVENTORY", "inventory.coverage", "Coverage must be explicitly argued for independent review.")
    usages = inventory.get("usages")
    if not isinstance(usages, list) or not usages:
        _issue(out, "INVALID_USAGES", "inventory.usages", "At least one supported usage is required.")
        return out
    occurrences = _occurrences(source)
    seen = set()
    for i, usage in enumerate(usages):
        path = f"inventory.usages[{i}]"
        if not isinstance(usage, dict):
            _issue(out, "INVALID_USAGE", path, "Usage must be an object.")
            continue
        uid = usage.get("usage_id")
        if not _text(uid) or uid in seen:
            _issue(out, "INVALID_USAGE_ID", path, "Usage identity is missing or duplicated.")
        if isinstance(uid, str):
            seen.add(uid)
        for field in ("sentence_a", "sentence_b", "argumentation"):
            if not _text(usage.get(field)):
                _issue(out, "MISSING_USAGE_ARGUMENTATION", f"{path}.{field}", "Every usage requires its own A/B and argumentation.")
        evidence = usage.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(_text(x) for x in evidence):
            _issue(out, "MISSING_USAGE_EVIDENCE", path, "Usage needs explicit supporting evidence.")
        env = _parameters(usage.get("parameters"), out, f"{path}.parameters", allow_empty=True)
        try:
            projection = prepare_parameter_projection(source, usage)
        except ValueError as exc:
            _issue(out, "INVALID_PARAMETER_PROJECTION", path, str(exc))
            continue
        parameter_ids = set(projection["parameter_occurrence_ids"])
        covered_determiners = set(projection["covered_determiner_ids"])
        for param in usage.get("parameters", []) if isinstance(usage.get("parameters"), list) else []:
            if isinstance(param, dict) and not _text(param.get("role")):
                _issue(out, "MISSING_PARAMETER_ROLE", path, "External parameter roles must be stated.")
        target_args = usage.get("target_arguments")
        if (not isinstance(target_args, list)
                or not all(isinstance(x, str) and x in env for x in target_args)
                or len(set(x for x in target_args if isinstance(x, str))) != len(target_args)):
            _issue(out, "INVALID_TARGET_ARGUMENTS", path, "Target arguments must reference distinct declared parameters.")
        occurrence_ids = usage.get("occurrence_ids")
        if (not isinstance(occurrence_ids, list) or not all(isinstance(x, str) and x in occurrences for x in occurrence_ids)):
            _issue(out, "UNKNOWN_USAGE_OCCURRENCE", path, "Usage source references must preserve fixed WSD.")
        if usage.get("voice") not in ("active", "passive"):
            _issue(out, "INVALID_VOICE", path, "Usage must explicitly state active or passive voice.")
        witnesses = usage.get("witnesses", [])
        witness_names = set()
        if not isinstance(witnesses, list):
            _issue(out, "INVALID_WITNESSES", path, "Witness declarations must be a list.")
            witnesses = []
        for j, witness in enumerate(witnesses):
            here = f"{path}.witnesses[{j}]"
            if not isinstance(witness, dict):
                _issue(out, "INVALID_WITNESS", here, "Witness must be an object.")
                continue
            name = witness.get("name")
            if not isinstance(name, str) or not _NAME.fullmatch(name) or name in witness_names:
                _issue(out, "INVALID_WITNESS", here, "Witness name is invalid or duplicated.")
            if isinstance(name, str) and name in env:
                _issue(out, "EXTERNAL_PARAMETER_CAPTURE", here, "External inputs must never become existential witnesses.")
            if isinstance(name, str):
                witness_names.add(name)
            occurrence_id = witness.get("occurrence_id")
            witness_origin = witness.get("origin")
            if not _basis(source, context) and witness.get("type") == "V" and witness_origin in {"a", "definition_internal"}:
                _issue(out, "NOUN_CANNOT_INTRODUCE_EVENT", here,
                       "A noun witness cannot introduce V; an event requires its own verb-occurrence binding mechanism.")
            occurrence = occurrences.get(occurrence_id) if isinstance(occurrence_id, str) else None
            if (not _type(witness.get("type")) or witness_origin not in ("a", "definition_internal")
                    or occurrence is None or not _text(witness.get("reason"))):
                _issue(out, "INVALID_WITNESS", here, "Witness needs typed definition evidence and a valid origin.")
            elif occurrence.get("text", "").casefold() == "the":
                _issue(out, "THE_CANNOT_BIND", here, "The article cannot supply an existential witness.")
            elif witness_origin == "a" and occurrence.get("text", "").casefold() not in {"a", "an"}:
                _issue(out, "INVALID_A_WITNESS_SOURCE", here, "An a witness must be aligned to the actual article.")
        determiners = usage.get("determiners", [])
        if not isinstance(determiners, list):
            _issue(out, "INVALID_DETERMINERS", path, "Determiner analysis must be a list.")
            determiners = []
        determiner_ids = set()
        raw_plan = usage.get("binding_plan", {})
        raw_scopes = raw_plan.get("scopes", []) if isinstance(raw_plan, dict) else []
        article_scope_names = {row.get("scope_id"): {p.get("name") for p in row.get("variables", []) if isinstance(p, dict)}
                               for row in raw_scopes if isinstance(row, dict)} if isinstance(raw_scopes, list) else {}
        for j, determiner in enumerate(determiners):
            here = f"{path}.determiners[{j}]"
            if not isinstance(determiner, dict):
                _issue(out, "INVALID_DETERMINER", here, "Determiner must be an object.")
                continue
            kind, action = determiner.get("kind"), determiner.get("action")
            determiner_id = determiner.get("occurrence_id")
            if isinstance(determiner_id, str) and determiner_id in covered_determiners:
                continue
            article_parameter_available = (determiner.get("parameter") in env
                or (kind == "the" and isinstance(determiner.get("scope_id"), str)
                    and determiner.get("parameter") in article_scope_names.get(determiner["scope_id"], set())))
            if isinstance(determiner_id, str):
                if determiner_id in determiner_ids:
                    _issue(out, "DUPLICATE_DETERMINER", here, "Each determiner occurrence needs exactly one decision.")
                determiner_ids.add(determiner_id)
            occurrence = occurrences.get(determiner_id) if isinstance(determiner_id, str) else None
            if occurrence is None:
                _issue(out, "UNKNOWN_DETERMINER_OCCURRENCE", here, "Determiner must retain its source occurrence.")
            elif occurrence.get("text", "").casefold() not in ({"a", "an"} if kind == "a" else {kind} if isinstance(kind, str) else set()):
                _issue(out, "DETERMINER_SURFACE_MISMATCH", here, "Determiner kind must match its actual source article or quantifier.")
            if kind in ("a", "the"):
                head = determiner.get("head_occurrence_id")
                if (not isinstance(head, str) or head not in occurrences or head == determiner_id
                        or head not in (occurrence_ids if isinstance(occurrence_ids, list) else [])):
                    _issue(out, "DETERMINER_HEAD_MISSING", here, "Article must identify its nominal head's fixed-WSD occurrence.")
                if kind == "the" and (not isinstance(determiner.get("parameter"), str) or not article_parameter_available):
                    _issue(out, "THE_EXTERNAL_PARAMETER_MISSING", here, "Dropping/sharing preserves the declared external or operator-bound noun parameter.")
            if kind == "all":
                if action == "basis_definition" and not _basis(source, context):
                    _issue(out, "NONBASIS_ALL_DEFINITION", here, "Only frozen basis membership licenses direct quantifier realization.")
                elif action not in ("provider", "basis_definition"):
                    _issue(out, "ALL_REQUIRES_PROVIDER", here, "All must use its own certified formula.")
            elif kind == "a":
                if action == "parameter":
                    parameter = determiner.get("parameter")
                    if not isinstance(parameter, str) or parameter not in env:
                        _issue(out, "A_EXTERNAL_PARAMETER_MISSING", here, "An external a noun must reuse a declared open parameter.")
                    if any(w.get("occurrence_id") == determiner.get("occurrence_id") for w in witnesses if isinstance(w, dict)):
                        _issue(out, "EXTERNAL_PARAMETER_CAPTURE", here, "An external a noun cannot also declare an existential witness.")
                elif action != "exists" or not any(w.get("origin") == "a" and w.get("occurrence_id") == determiner.get("occurrence_id") for w in witnesses if isinstance(w, dict)):
                    _issue(out, "A_REQUIRES_INTERNAL_WITNESS", here, "A introduces a declared internal witness, never an external input.")
            elif kind == "the":
                if action not in ("share", "drop"):
                    _issue(out, "THE_CANNOT_BIND", here, "The only shares an existing parameter or is removed.")
                elif action == "share" and (not isinstance(determiner.get("parameter"), str)
                        or not article_parameter_available or determiner.get("parameter") != determiner.get("antecedent")):
                    _issue(out, "THE_REQUIRES_SHARED_PARAMETER", here, "Coreference must reuse the same existing noun parameter.")
                elif action == "drop" and determiner.get("antecedent") is not None:
                    _issue(out, "THE_DROP_WITH_ANTECEDENT", here, "A recorded antecedent must be shared, not discarded.")
            else:
                _issue(out, "INVALID_DETERMINER", here, "Only a, the and all have declared determiner handling.")
        required_determiners = {oid for oid, occurrence in occurrences.items()
                               if occurrence.get("text", "").casefold() in {"a", "an", "the", "all"}
                               and oid not in covered_determiners}
        exclusions = usage.get("determiner_exclusions", [])
        excluded_ids = set()
        if not isinstance(exclusions, list):
            _issue(out, "INVALID_DETERMINER_EXCLUSIONS", path, "Exclusions require independent applicability review.")
            exclusions = []
        for exclusion in exclusions:
            if (not isinstance(exclusion, dict) or set(exclusion) != {"occurrence_id", "reason"}
                    or not isinstance(exclusion.get("occurrence_id"), str)
                    or exclusion["occurrence_id"] not in required_determiners or not _text(exclusion.get("reason"))):
                _issue(out, "INVALID_DETERMINER_EXCLUSION", path, "An exclusion must identify a real determiner and state a substantive applicability reason.")
                continue
            oid = exclusion["occurrence_id"]
            if oid in excluded_ids or oid in determiner_ids:
                _issue(out, "DUPLICATE_DETERMINER_DECISION", path, "A determiner cannot be excluded twice or both analyzed and excluded.")
            excluded_ids.add(oid)
        if required_determiners != determiner_ids | excluded_ids:
            _issue(out, "DETERMINER_COVERAGE_MISMATCH", path, "Every source a/the/all occurrence needs exactly one analysis or independently reviewed exclusion.")
        plan = usage.get("binding_plan")
        if (not isinstance(plan, dict) or set(plan) - {"lexical", "structural", "scopes"}
                or not isinstance(plan.get("lexical"), list) or not isinstance(plan.get("structural"), dict)
                or set(plan["structural"]) != {"lhs", "rhs"}
                or not all(isinstance(plan["structural"].get(side), list) for side in ("lhs", "rhs"))):
            _issue(out, "INVALID_BINDING_PLAN", path, "A verifier-reviewed lexical and side-specific structural binding plan is required.")
            continue
        protected = {**env, **{w["name"]: w.get("type") for w in witnesses if isinstance(w, dict) and isinstance(w.get("name"), str)}}
        scope_specs, scope_environments = _binding_scopes(plan, protected, out, f"{path}.binding_plan.scopes")
        plan_hashes = set()
        for j, binding in enumerate(plan["lexical"]):
            here = f"{path}.binding_plan.lexical[{j}]"
            if (not isinstance(binding, dict) or set(binding) - {"occurrence_id", "usage_id", "bindings", "scope_id"}
                    or binding.get("occurrence_id") not in occurrences or not isinstance(binding.get("usage_id"), str)
                    or not isinstance(binding.get("bindings"), dict)):
                _issue(out, "INVALID_LEXICAL_BINDING", here, "Binding must select a source occurrence, approved usage and parameter map.")
                continue
            scope = binding.get("scope_id")
            if scope is not None and scope not in scope_environments:
                _issue(out, "UNKNOWN_BINDING_SCOPE", here, "Lexical binding refers to an undeclared local scope.")
                continue
            binding_environment = protected if scope is None else scope_environments[scope]
            oid = binding["occurrence_id"]
            if oid not in occurrence_ids:
                _issue(out, "INVALID_LEXICAL_BINDING", here, "Lexical binding is outside this usage's source occurrences.")
            if oid in excluded_ids:
                _issue(out, "EXCLUDED_DETERMINER_CALLED", here, "Excluded determiner occurrences cannot supply lexical calls.")
            if oid in parameter_ids:
                _issue(out, "PARAMETER_PHRASE_CALLED", here, "Argumentation parameter words are not lexical conditions.")
            key = provider_key(occurrences[oid]["synset_id"], binding["usage_id"])
            provider = context.get("providers", {}).get(key)
            if not isinstance(provider, dict):
                _issue(out, "PROVIDER_MISSING", here, f"Binding provider is unavailable: {key}")
                continue
            provider_types = {p["name"]: p.get("type") for p in provider.get("parameters", []) if isinstance(p, dict) and "name" in p}
            for k, value in binding["bindings"].items():
                if k not in provider_types:
                    _issue(out, "INVALID_LEXICAL_BINDING", here, "Unknown provider parameter.")
                elif isinstance(value, str):
                    if value not in binding_environment:
                        _issue(out, "INVALID_LEXICAL_BINDING", here, "Binding variable is unavailable.")
                    elif binding_environment[value] != provider_types[k]:
                        _issue(out, "LEXICAL_BINDING_TYPE_MISMATCH", here, "Direct bindings must preserve exact types.")
                elif (not isinstance(value, dict) or set(value) != {"world_of"}
                      or not isinstance(value.get("world_of"), str)
                      or provider_types[k] != "World" or binding_environment.get(value["world_of"]) != "V"):
                    _issue(out, "INVALID_WORLD_BINDING", here, "World(e) fills only a World-typed lexical slot with a visible event.")
            digest = canonical_hash(binding)
            if digest in plan_hashes:
                _issue(out, "DUPLICATE_LEXICAL_BINDING", here, "Duplicate binding plan entry.")
            plan_hashes.add(digest)
        for side in ("lhs", "rhs"):
            seen_atoms = set()
            for j, binding in enumerate(plan["structural"][side]):
                here = f"{path}.binding_plan.structural.{side}[{j}]"
                try:
                    if not isinstance(binding, dict) or set(binding) - {"name", "arguments", "scope_id"} or not isinstance(binding.get("arguments"), list):
                        raise ValueError("Invalid structural commitment")
                    scope = binding.get("scope_id")
                    if scope is not None and (side == "lhs" or scope not in scope_environments):
                        raise ValueError("Unknown or illegal structural scope")
                    binding_environment = protected if scope is None else scope_environments[scope]
                    atom = _plan_atom(binding)
                    relation = context.get("structures", {}).get("relations", {}).get(binding["name"])
                    if not isinstance(relation, dict) or relation.get("return_type") != "Prop":
                        raise ValueError("Structural commitment must be an allowed proposition")
                    if _free(atom) - set(binding_environment) or (side == "lhs" and _free(atom) - set(env)):
                        raise ValueError("Structural commitment uses undeclared or improperly scoped variables")
                    types = []
                    for argument in binding["arguments"]:
                        if isinstance(argument, str):
                            types.append(binding_environment[argument])
                        else:
                            if binding_environment[argument["implicit_subject"]] != "V":
                                raise ValueError("Implicit subject requires an event")
                            types.append("E")
                    if len(types) != len(relation.get("argument_types", [])) or any(not _matches(t, expected) for t, expected in zip(types, relation["argument_types"])):
                        raise ValueError("Structural commitment has incompatible types")
                    scoped_digest = canonical_hash({"scope_id": scope, "atom": atom})
                    if scoped_digest in seen_atoms:
                        raise ValueError("Duplicate structural commitment")
                    seen_atoms.add(scoped_digest)
                except (ValueError, TypeError, KeyError):
                    _issue(out, "INVALID_STRUCTURAL_BINDING", here, "Invalid side-specific structural argument plan.")
        if not _basis(source, context):
            for determiner in determiners:
                if determiner.get("occurrence_id") in covered_determiners:
                    continue
                if determiner.get("kind") not in ("a", "the"):
                    continue
                required_names = ({determiner.get("parameter")} if determiner.get("kind") == "the" or determiner.get("action") == "parameter"
                                  else {w.get("name") for w in witnesses if isinstance(w, dict) and w.get("occurrence_id") == determiner.get("occurrence_id")})
                planned_names = {name for b in plan["lexical"] if isinstance(b, dict) and b.get("occurrence_id") == determiner.get("head_occurrence_id")
                                 for name in b.get("bindings", {}).values() if isinstance(name, str)}
                if not required_names or not required_names.issubset(planned_names):
                    _issue(out, "DETERMINER_HEAD_BINDING_MISMATCH", path, "Nominal head must receive the article's shared external parameter or declared internal witness.")
    if not out:
        signature = None
        for i, usage in enumerate(usages):
            environment = {p["name"]: p["type"] for p in usage["parameters"]}
            current = [environment[name] for name in usage["target_arguments"]]
            if signature is None:
                signature = current
            elif current != signature:
                _issue(out, "CORE_TARGET_SIGNATURE_MISMATCH", f"inventory.usages[{i}].target_arguments",
                       "One shared synset target must have one inferred core signature; full usage roles may differ.")
    return out


def _provider(call: dict, context: dict, round_number: int | None = None) -> dict:
    key = provider_key(call.get("synset_id", ""), call.get("usage_id", ""))
    record = context.get("providers", {}).get(key)
    if not isinstance(record, dict):
        raise ValueError(f"PROVIDER_MISSING: {key}")
    if record.get("synset_id") != call.get("synset_id") or record.get("usage_id") != call.get("usage_id"):
        raise ValueError(f"PROVIDER_ID_MISMATCH: {key}")
    if (not isinstance(record.get("lhs"), dict) or not isinstance(record.get("rhs"), dict)
            or not isinstance(record.get("parameters"), list)):
        raise ValueError(f"PROVIDER_INCOMPLETE: {key}")
    if not _text(record.get("bundle_hash")) or call.get("provider_hash") != record["bundle_hash"]:
        raise ValueError(f"PROVIDER_HASH_MISMATCH: {key}")
    current_round = context.get("round", 0) if round_number is None else round_number
    if type(record.get("round")) is not int or type(current_round) is not int or record["round"] >= current_round:
        raise ValueError(f"PROVIDER_NOT_EARLIER: {key}")
    is_basis = record.get("synset_id") in context.get("basis_ids", [])
    if type(record.get("is_basis")) is not bool or record["is_basis"] != is_basis:
        raise ValueError(f"PROVIDER_BASIS_MISMATCH: {key}")
    if record.get("mode") != context.get("mode", "production"):
        raise ValueError(f"PROVIDER_MODE_MISMATCH: {key}")
    return record


class _Checker:
    def __init__(self, source: dict, usage: dict, candidate: dict, context: dict, out: list):
        self.source, self.usage, self.candidate, self.context, self.out = source, usage, candidate, context, out
        self.basis = _basis(source, context)
        self.external = {p["name"]: p["type"] for p in usage.get("parameters", []) if isinstance(p, dict) and "name" in p and "type" in p}
        self.occurrences = _occurrences(source)
        self.parameter_projection = prepare_parameter_projection(source, usage)
        self.primitives = {}
        self.targets = 0
        self.calls = []
        self.binders = []
        self.plan = usage["binding_plan"]
        self.protected = set(self.external) | {w["name"] for w in usage.get("witnesses", [])}
        global_environment = {**self.external, **{w["name"]: w["type"] for w in usage.get("witnesses", [])}}
        self.scope_specs, self.scope_environments = _binding_scopes(self.plan, global_environment, out, "formula.binding_plan.scopes")
        self.scope_stack = []
        self.realized_scopes = {}
        self.realized_lexical = set()
        self.realized_structural = {"lhs": set(), "rhs": set()}
        self.meaningful_external = set()
        raw = candidate.get("primitives", [])
        if not isinstance(raw, list):
            _issue(out, "INVALID_PRIMITIVES", "formula.primitives", "Primitive declarations must be a list.")
            raw = []
        if raw and not self.basis:
            _issue(out, "NONBASIS_PRIMITIVE_DECLARATION", "formula.primitives", "Only authenticated basis definitions can introduce primitives.")
        for i, primitive in enumerate(raw):
            path = f"formula.primitives[{i}]"
            if not isinstance(primitive, dict):
                _issue(out, "INVALID_PRIMITIVE", path, "Primitive must be an object.")
                continue
            name = primitive.get("name")
            configured_structures = self.context.get("structures", {}).get("relations", {})
            if (not isinstance(name, str) or not _NAME.fullmatch(name) or name in self.primitives
                    or name in _STRUCTURES or name in configured_structures or name in _NOMINALIZATION_INTERNAL_SYMBOLS):
                _issue(out, "INVALID_PRIMITIVE_NAME", path, "Primitive name is invalid, duplicated, or shadows a structure.")
                continue
            if set(primitive) - {"name", "argument_types", "return_type", "meaning", "source_evidence"}:
                _issue(out, "INVALID_PRIMITIVE", path, "Primitive declarations cannot contain hidden formulas or extra semantic fields.")
            args = primitive.get("argument_types")
            if (not isinstance(args, list) or not all(_type(t) for t in args)
                    or not _type(primitive.get("return_type"))
                    or not _text(primitive.get("meaning")) or not _text(primitive.get("source_evidence"))):
                _issue(out, "INVALID_PRIMITIVE", path, "Primitive requires a typed signature, meaning and basis evidence.")
                continue
            self.primitives[name] = primitive

    def error(self, code: str, path: str, message: str):
        _issue(self.out, code, path, message)

    def expected(self, actual: Any, expected: Any, path: str):
        if actual is not None and not _matches(actual, expected):
            self.error("TYPE_MISMATCH", path, f"Expected {expected!r}; got {actual!r}. No E/V coercion is allowed.")

    def fields(self, node: dict, allowed: set, path: str):
        unknown = set(node) - allowed
        if unknown:
            self.error("UNSUPPORTED_AST_FIELD", path, f"Undeclared AST fields: {sorted(unknown)}")

    def structure_binding(self, node: dict, side: str, path: str, *, authored=True):
        if node.get("name") in {"ImplicitSubj", "World"}:
            return
        active_names = set(self.scope_environments[self.scope_stack[-1]]) if self.scope_stack else self.protected
        protected = _free(node) & active_names
        matching = [i for i, row in enumerate(self.plan["structural"][side]) if _plan_atom(row) == node
                    and (row.get("scope_id") is None or row["scope_id"] in self.scope_stack)]
        if matching:
            self.realized_structural[side].update(matching)
            if side == "rhs":
                self.meaningful_external |= protected & set(self.external)
        elif authored and protected:
            # A basis may compute a structural term with its internal primitive;
            # its novel semantics still requires the independent basis review.
            computed_basis_term = self.basis and any(a.get("op") == "primitive" for a in node.get("args", []) if isinstance(a, dict))
            if not computed_basis_term:
                self.error("STRUCTURAL_BINDING_MISMATCH", path, "Authored structural roles must preserve the independently approved side-specific arguments.")

    def lexical_binding(self, node: dict, record: dict, path: str):
        args = node.get("args", [])
        parameters = record["parameters"]
        if not isinstance(args, list) or len(args) != len(parameters):
            return
        actual = {p["name"]: arg for p, arg in zip(parameters, args)}
        active_names = set(self.scope_environments[self.scope_stack[-1]]) if self.scope_stack else self.protected
        required = {key: arg["var"] for key, arg in actual.items()
                    if isinstance(arg, dict) and set(arg) == {"var"} and arg["var"] in active_names}
        for key, arg in actual.items():
            if (isinstance(arg, dict) and arg.get("op") == "struct" and arg.get("name") == "World"
                    and isinstance(arg.get("args"), list) and len(arg["args"]) == 1
                    and isinstance(arg["args"][0], dict) and set(arg["args"][0]) == {"var"}):
                required[key] = {"world_of": arg["args"][0]["var"]}
        matches = []
        for i, row in enumerate(self.plan["lexical"]):
            if row["occurrence_id"] != node.get("occurrence_id") or row["usage_id"] != node.get("usage_id"):
                continue
            if row.get("scope_id") is not None and row["scope_id"] not in self.scope_stack:
                continue
            if (all(actual.get(key) == _plan_term(name) for key, name in row["bindings"].items())
                    and all(row["bindings"].get(key) == name for key, name in required.items())):
                matches.append(i)
        if not matches:
            self.error("LEXICAL_BINDING_MISMATCH", path, "Call arguments must match a certified occurrence/usage binding plan; external inputs cannot be replaced by witnesses.")
            return
        self.realized_lexical.update(matches)
        for value in required.values():
            name = value if isinstance(value, str) else value["world_of"]
            if name in self.external:
                self.meaningful_external.add(name)
        # Complete provider LHS roles can realize RHS role commitments; the
        # macro itself already preserves every provider parameter binding.
        try:
            pattern = instantiate_provider_call(node, self.context)
            for atom in _walk(pattern):
                if atom.get("op") == "struct":
                    self.structure_binding(atom, "rhs", path, authored=False)
        except (ValueError, TypeError, KeyError) as exc:
            self.error("PROVIDER_PATTERN_INVALID", path, str(exc))

    def call_args(self, node: dict, signature: list, env: dict, path: str, side: str):
        args = node.get("args")
        if not isinstance(args, list) or len(args) != len(signature):
            self.error("CALL_ARITY_MISMATCH", path, "Call must instantiate every approved parameter exactly once in order.")
            return
        for i, (arg, expected) in enumerate(zip(args, signature)):
            actual = self.infer(arg, env, f"{path}.args[{i}]", side, node, i)
            self.expected(actual, expected, f"{path}.args[{i}]")

    def infer(self, node: Any, env: dict, path: str, side: str, parent: dict | None = None, index: int | None = None):
        if not isinstance(node, dict):
            self.error("INVALID_AST", path, "AST nodes must be explicit objects; literals are not allowed.")
            return None
        if "var" in node:
            self.fields(node, {"var"}, path)
            name = node.get("var")
            if not isinstance(name, str) or name not in env:
                self.error("UNBOUND_VARIABLE", path, f"Undeclared variable {name!r}.")
                return None
            return env[name]
        op = node.get("op")
        if not isinstance(op, str):
            self.error("UNKNOWN_AST_OPERATION", path, "AST operation must be an explicit string.")
            return None
        if side == "lhs" and op not in {"target", "and", "struct"}:
            self.error("INVALID_LHS_SHAPE", path, "LHS must be one positive target with its complete structural role pattern.")
        if op == "target":
            self.fields(node, {"op", "args"}, path)
            self.targets += 1
            if side != "lhs":
                self.error("TARGET_ON_RHS", path, "Own target is only legal in its LHS pattern.")
            expected_args = [{"var": name} for name in self.usage.get("target_arguments", [])]
            if node.get("args") != expected_args:
                self.error("TARGET_PATTERN_MISMATCH", path, "Target arguments must match the certified usage declaration.")
            for i, arg in enumerate(node.get("args", []) if isinstance(node.get("args"), list) else []):
                self.infer(arg, env, f"{path}.args[{i}]", side)
            return "Prop"
        if op == "struct":
            self.fields(node, {"op", "name", "args"}, path)
            name = node.get("name")
            relations = self.context.get("structures", {}).get("relations", {})
            relation = relations.get(name) if isinstance(name, str) else None
            if not isinstance(relation, dict):
                self.error("STRUCTURE_NOT_ALLOWED", path, "Structural relation is not in the frozen allowlist.")
                return None
            signature = relation.get("argument_types")
            if not isinstance(signature, list) or not _type(relation.get("return_type")):
                self.error("INVALID_STRUCTURE_CONFIG", path, "Malformed structural relation signature.")
                return None
            args = node.get("args")
            if name == "World":
                provider = None
                if isinstance(parent, dict) and parent.get("op") == "use":
                    provider = self.context.get("providers", {}).get(provider_key(parent.get("synset_id", ""), parent.get("usage_id", "")))
                params = provider.get("parameters", []) if isinstance(provider, dict) else []
                if not (isinstance(index, int) and 0 <= index < len(params) and params[index].get("type") == "World"):
                    self.error("WORLD_REQUIRES_LEXICAL_SLOT", path, "World(e) is a repeatable argument term only in an existing lexical World slot.")
            if not isinstance(args, list) or len(args) != len(signature):
                self.error("CALL_ARITY_MISMATCH", path, "Structural relation arity mismatch.")
            else:
                for i, (arg, expected) in enumerate(zip(args, signature)):
                    actual = self.infer(arg, env, f"{path}.args[{i}]", side, node, i)
                    self.expected(actual, expected, f"{path}.args[{i}]")
            if name == "ImplicitSubj" or relation.get("passive_only"):
                if self.usage.get("voice") != "passive":
                    self.error("IMPLICIT_SUBJECT_REQUIRES_PASSIVE", path, "ImplicitSubj is reserved for passive usage.")
                if (name == "ImplicitSubj" and (not isinstance(parent, dict) or parent.get("op") != "struct"
                        or parent.get("name") != "Agent" or index != 1
                        or not isinstance(args, list) or len(args) != 1
                        or args[0] != parent.get("args", [None])[0])):
                    self.error("INVALID_IMPLICIT_SUBJECT_POSITION", path, "Only Agent(e, ImplicitSubj(e)) is permitted.")
            if relation["return_type"] == "Prop":
                self.structure_binding(node, side, path)
            return relation["return_type"]
        if op == "primitive":
            self.fields(node, {"op", "name", "args"}, path)
            if not self.basis:
                self.error("NONBASIS_PRIMITIVE", path, "Nonbasis formulas cannot directly use semantic primitives, even registered ones.")
            declaration = self.primitives.get(node.get("name")) if isinstance(node.get("name"), str) else None
            if declaration is None:
                self.error("UNDECLARED_PRIMITIVE", path, "Primitive must be declared in this basis implementation.")
                return None
            self.call_args(node, declaration["argument_types"], env, path, side)
            if side == "rhs" and self.basis:
                self.meaningful_external |= {arg["var"] for arg in node.get("args", [])
                                            if isinstance(arg, dict) and set(arg) == {"var"} and arg["var"] in self.external}
            return declaration["return_type"]
        if op == "use":
            self.fields(node, {"op", "synset_id", "usage_id", "provider_hash", "occurrence_id", "args"}, path)
            occurrence = self.occurrences.get(node.get("occurrence_id")) if isinstance(node.get("occurrence_id"), str) else None
            if node.get("occurrence_id") in self.parameter_projection["parameter_occurrence_ids"]:
                self.error("PARAMETER_PHRASE_CALLED", path, "Parameter placeholder words cannot be logicized as predicates.")
            if any(item["occurrence_id"] == node.get("occurrence_id") for item in self.usage.get("determiner_exclusions", [])):
                self.error("EXCLUDED_DETERMINER_CALLED", path, "A declared inapplicable determiner cannot be called in this usage.")
            if not self.basis:
                if occurrence is None or occurrence.get("synset_id") != node.get("synset_id"):
                    self.error("SOURCE_SYNSET_MISMATCH", path, "Direct call must match a fixed-WSD definition occurrence.")
                if node.get("occurrence_id") not in self.usage.get("occurrence_ids", []):
                    self.error("CALL_OUTSIDE_USAGE_SOURCE", path, "Call occurrence is absent from this usage's certified argumentation.")
            try:
                record = _provider(node, self.context)
            except (ValueError, TypeError) as exc:
                message = str(exc)
                self.error(message.split(":", 1)[0], path, message)
                return None
            self.calls.append(node)
            signature = [p.get("type") for p in record["parameters"] if isinstance(p, dict)]
            if len(signature) != len(record["parameters"]) or not all(_type(t) for t in signature):
                self.error("PROVIDER_INCOMPLETE", path, "Provider has invalid parameter types.")
                return None
            self.call_args(node, signature, env, path, side)
            self.lexical_binding(node, record, path)
            return "Prop"
        if op in {"and", "or"}:
            self.fields(node, {"op", "args"}, path)
            args = node.get("args")
            if not isinstance(args, list) or len(args) < 2:
                self.error("INVALID_CONNECTIVE", path, "And/or require at least two explicit formulas.")
            else:
                for i, arg in enumerate(args):
                    self.expected(self.infer(arg, env, f"{path}.args[{i}]", side), "Prop", path)
            return "Prop"
        if op == "not":
            self.fields(node, {"op", "body"}, path)
            self.expected(self.infer(node.get("body"), env, f"{path}.body", side), "Prop", path)
            return "Prop"
        if op == "at_world":
            self.fields(node, {"op", "world", "body"}, path)
            if not self.basis:
                self.error("NONBASIS_WORLD_CONTEXT", path, "World evaluation belongs to the supplied basis definition, not a new caller operator.")
            self.expected(self.infer(node.get("world"), env, f"{path}.world", side), "World", path)
            world = node.get("world")
            if (side == "rhs" and self.basis and isinstance(world, dict) and set(world) == {"var"}
                    and self.external.get(world["var"]) == "World"):
                self.meaningful_external.add(world["var"])
            self.expected(self.infer(node.get("body"), env, f"{path}.body", side), "Prop", path)
            return "Prop"
        if op in {"implies", "iff", "eq"}:
            self.fields(node, {"op", "left", "right"}, path)
            left = self.infer(node.get("left"), env, f"{path}.left", side)
            right = self.infer(node.get("right"), env, f"{path}.right", side)
            if op == "eq":
                if left is not None and right is not None and left != right:
                    self.error("TYPE_MISMATCH", path, "Equality operands have different types.")
            else:
                self.expected(left, "Prop", path)
                self.expected(right, "Prop", path)
            return "Prop"
        if op in {"exists", "forall", "lambda"}:
            key = "parameters" if op == "lambda" else "variables"
            allowed = {"op", key, "body"} | ({"origin", "occurrence_id"} if op != "lambda" else set())
            if op in {"lambda", "forall"}:
                allowed.add("scope_id")
            self.fields(node, allowed, path)
            local = _parameters(node.get(key), self.out, f"{path}.{key}")
            for name in local:
                if name in env:
                    self.error("EXTERNAL_PARAMETER_CAPTURE" if name in self.external else "VARIABLE_SHADOWING", path, "Local binders cannot capture or shadow existing variables.")
            if op == "forall" and not self.basis:
                self.error("NONBASIS_FORALL", path, "All must invoke its lexical provider; native universal quantification is basis-only.")
            if op == "exists":
                self.binders.append(node)
            if op == "exists" and not self.basis:
                witnesses = {w.get("name"): w for w in self.usage.get("witnesses", []) if isinstance(w, dict)}
                for name, kind in local.items():
                    witness = witnesses.get(name)
                    if (not witness or witness.get("type") != kind or node.get("origin") != witness.get("origin")
                            or node.get("occurrence_id") != witness.get("occurrence_id")):
                        self.error("UNAPPROVED_EXISTENTIAL", path, "Every existential needs an independently reviewed internal witness declaration.")
                if node.get("origin") not in ("a", "definition_internal"):
                    self.error("INVALID_EXISTENTIAL_ORIGIN", path, "The cannot introduce a witness; only declared internal witnesses may bind.")
            scope_id = node.get("scope_id")
            entered_scope = False
            if scope_id is not None:
                declaration = self.scope_specs.get(scope_id) if isinstance(scope_id, str) else None
                if declaration is None:
                    self.error("UNKNOWN_BINDER_SCOPE", path, "Binder's local scope is not certified in the usage plan.")
                else:
                    declared_variables = [{"name": p["name"], "type": p["type"]} for p in declaration["variables"]]
                    actual_variables = [{"name": name, "type": kind} for name, kind in local.items()]
                    parent = self.scope_stack[-1] if self.scope_stack else None
                    if declaration["kind"] != op or declaration["parent_scope"] != parent or declared_variables != actual_variables:
                        self.error("BINDER_SCOPE_MISMATCH", path, "Binder kind, parent, ordered local names and types must match the certified scope.")
                    else:
                        self.realized_scopes[scope_id] = self.realized_scopes.get(scope_id, 0) + 1
                        self.scope_stack.append(scope_id)
                        entered_scope = True
            try:
                body_type = self.infer(node.get("body"), {**env, **local}, f"{path}.body", side)
            finally:
                if entered_scope:
                    self.scope_stack.pop()
            if op == "lambda":
                return {"arrow": list(local.values()) + [body_type]} if body_type is not None else None
            self.expected(body_type, "Prop", path)
            return "Prop"
        if op == "apply":
            self.fields(node, {"op", "function", "args"}, path)
            function_type = self.infer(node.get("function"), env, f"{path}.function", side)
            if not isinstance(function_type, dict) or "arrow" not in function_type:
                self.error("NOT_A_FUNCTION", path, "Apply requires a typed function or lambda.")
                return None
            self.call_args(node, function_type["arrow"][:-1], env, path, side)
            if side == "rhs":
                self.meaningful_external |= {term["var"] for term in [node.get("function"), *node.get("args", [])]
                                            if isinstance(term, dict) and set(term) == {"var"} and term["var"] in self.external}
            return function_type["arrow"][-1]
        self.error("UNKNOWN_AST_OPERATION", path, f"Operation {op!r} is not in the V3 language.")
        return None


@_fail_closed
def validate_formula(source: dict, inventory: dict, candidate: dict, context: dict) -> list:
    out = validate_inventory(source, inventory, context)
    if not isinstance(source, dict) or not isinstance(inventory, dict):
        return out
    if not isinstance(candidate, dict):
        _issue(out, "INVALID_FORMULA", "formula", "Formula candidate must be an object.")
        return out
    unknown = set(candidate) - {"synset_id", "usage_id", "parameters", "lhs", "rhs", "primitives", "notes"}
    if unknown:
        _issue(out, "UNSUPPORTED_FORMULA_FIELD", "formula", f"Candidate cannot introduce its own source, inventory or hidden formulas: {sorted(unknown)}")
    if "notes" in candidate and not isinstance(candidate["notes"], str):
        _issue(out, "INVALID_FORMULA_NOTES", "formula.notes", "Notes must be textual metadata, not an AST.")
    if candidate.get("synset_id") != source.get("synset_id"):
        _issue(out, "FORMULA_SOURCE_MISMATCH", "formula.synset_id", "Candidate cannot change source identity.")
    rows = inventory.get("usages", []) if isinstance(inventory, dict) else []
    rows = rows if isinstance(rows, list) else []
    matching = [u for u in rows if isinstance(u, dict) and u.get("usage_id") == candidate.get("usage_id")]
    if len(matching) != 1:
        _issue(out, "UNKNOWN_FORMULA_USAGE", "formula.usage_id", "Formula must target exactly one certified usage.")
        return out
    usage = matching[0]
    if candidate.get("parameters") != usage.get("parameters"):
        _issue(out, "FORMULA_PARAMETER_MISMATCH", "formula.parameters", "External parameter declarations must exactly match the inventory.")
    # Do not attempt deeper interpretation of malformed inventory structures.
    if out:
        return out
    checker = _Checker(source, usage, candidate, context, out)
    lhs_type = checker.infer(candidate.get("lhs"), checker.external, "formula.lhs", "lhs")
    rhs_type = checker.infer(candidate.get("rhs"), checker.external, "formula.rhs", "rhs")
    checker.expected(lhs_type, "Prop", "formula.lhs")
    checker.expected(rhs_type, "Prop", "formula.rhs")
    if checker.targets != 1:
        checker.error("LHS_TARGET_COUNT", "formula.lhs", "A usage requires exactly one own-target occurrence, on the LHS.")
    for side in ("lhs", "rhs"):
        missing = set(checker.external) - _free(candidate.get(side))
        if missing:
            checker.error("EXTERNAL_PARAMETER_LOSS", f"formula.{side}", f"External input(s) missing or rebound: {sorted(missing)}")
        unrealized = set(range(len(checker.plan["structural"][side]))) - checker.realized_structural[side]
        if unrealized:
            checker.error("STRUCTURAL_BINDING_UNREALIZED", f"formula.{side}", "A certified structural role/parameter commitment was not realized.")
    if set(range(len(checker.plan["lexical"]))) - checker.realized_lexical:
        checker.error("LEXICAL_BINDING_UNREALIZED", "formula.rhs", "A certified lexical argument binding was omitted or changed.")
    for scope_id in checker.scope_specs:
        if checker.realized_scopes.get(scope_id, 0) != 1:
            checker.error("BINDING_SCOPE_REALIZATION_COUNT", "formula.rhs", f"Certified scope {scope_id!r} requires exactly one matching local binder.")
    if set(checker.external) - checker.meaningful_external:
        checker.error("EXTERNAL_SEMANTIC_FLOW_MISSING", "formula.rhs", "External inputs must reach certified lexical/structural positions or basis primitive arguments; mere equality/free occurrence is insufficient.")
    for witness in usage.get("witnesses", []):
        bindings = [b for b in checker.binders for v in b.get("variables", []) if v.get("name") == witness["name"]]
        if len(bindings) != 1:
            checker.error("WITNESS_BINDING_COUNT", "formula.rhs", f"Internal witness {witness['name']!r} requires exactly one binder, found {len(bindings)}.")
        elif (bindings[0].get("origin") != witness["origin"] or bindings[0].get("occurrence_id") != witness["occurrence_id"]):
            checker.error("WITNESS_BINDING_SOURCE_MISMATCH", "formula.rhs", "Witness binder must retain its certified origin and source occurrence.")
        else:
            bound_type = next(v.get("type") for v in bindings[0]["variables"] if v.get("name") == witness["name"])
            if bound_type != witness["type"]:
                checker.error("WITNESS_BINDING_TYPE_MISMATCH", "formula.rhs", "Witness binder must retain its certified type, including inside basis.")
            if witness["name"] not in _free(bindings[0].get("body")):
                checker.error("WITNESS_UNUSED", "formula.rhs", "A declared witness cannot be replaced by a vacuous binder.")
    for determiner in usage.get("determiners", []):
        occurrence = determiner["occurrence_id"]
        if occurrence in checker.parameter_projection["covered_determiner_ids"]:
            continue
        if determiner["kind"] == "all" and determiner["action"] == "provider" and not any(c.get("occurrence_id") == occurrence for c in checker.calls):
            checker.error("ALL_PROVIDER_MISSING", "formula.rhs", "The certified all occurrence must call its provider.")
        if determiner["kind"] == "a" and determiner["action"] == "exists" and not any(b.get("origin") == "a" and b.get("occurrence_id") == occurrence for b in checker.binders):
            checker.error("A_EXISTENTIAL_MISSING", "formula.rhs", "The internal a witness must be explicitly existentially bound.")
    if not out:
        try:
            expand_formula(candidate, context)
        except (ValueError, TypeError, KeyError) as exc:
            message = str(exc)
            checker.error(message.split(":", 1)[0], "formula.rhs", message)
    return out


@_fail_closed
def validate_bundle_formulas(source: dict, inventory: dict, formulas: list, context: dict, *, require_complete: bool = True) -> list:
    """Check one synset's complete usage bundle without imposing POS templates.

    Full usage parameters and role graphs may differ, and different usages may
    reduce to identical formulas.  The shared core target still needs one type
    signature; equally named basis primitives share one typed interpretation.
    """
    out = validate_inventory(source, inventory, context)
    if out:
        return out
    if not isinstance(formulas, list):
        _issue(out, "INVALID_FORMULA_BUNDLE", "formulas", "A complete formula list is required.")
        return out
    expected = {usage["usage_id"] for usage in inventory["usages"]}
    actual = [formula.get("usage_id") for formula in formulas if isinstance(formula, dict)]
    if (len(actual) != len(formulas) or not all(isinstance(uid, str) for uid in actual)
            or (set(actual) != expected if require_complete else not set(actual).issubset(expected))):
        _issue(out, "INCOMPLETE_USAGE_BUNDLE", "formulas", "Every declared usage requires its own accepted formula.")
        return out
    if len(set(actual)) != len(actual):
        _issue(out, "DUPLICATE_FORMULA_USAGE", "formulas", "Each usage must have exactly one formula.")
    for i, formula in enumerate(formulas):
        for issue in validate_formula(source, inventory, formula, context):
            out.append({**issue, "path": f"formulas[{i}].{issue['path']}"})
    target_signature = None
    for i, usage in enumerate(inventory["usages"]):
        environment = {p["name"]: p["type"] for p in usage["parameters"]}
        signature = [environment[name] for name in usage["target_arguments"]]
        if target_signature is None:
            target_signature = signature
        elif signature != target_signature:
            _issue(out, "CORE_TARGET_SIGNATURE_MISMATCH", f"inventory.usages[{i}].target_arguments",
                   "One synset's shared target must have one inferred core signature; role patterns may vary.")
    primitives = {}
    for i, formula in enumerate(formulas):
        for primitive in formula.get("primitives", []):
            if not isinstance(primitive, dict) or not isinstance(primitive.get("name"), str):
                continue
            name = primitive["name"]
            identity = {key: primitive.get(key) for key in ("argument_types", "return_type", "meaning")}
            if name in primitives and primitives[name] != identity:
                _issue(out, "SHARED_PRIMITIVE_CONFLICT", f"formulas[{i}].primitives",
                       f"Basis primitive {name!r} must preserve its earlier declaration {primitives[name]!r}; got {identity!r}.")
            else:
                primitives[name] = identity
    return out


class _Expander:
    def __init__(self, context: dict, candidate: dict):
        self.context = context
        self.used = {n.get("var") for n in _walk(candidate) if isinstance(n.get("var"), str)}
        self.used |= {n.get("name") for n in _walk(candidate) if isinstance(n.get("name"), str)}
        self.counter = 0

    def fresh(self, old: str) -> str:
        while True:
            self.counter += 1
            name = f"_v3_{self.counter}_{old}"
            if name not in self.used:
                self.used.add(name)
                return name

    def substitute(self, node: Any, substitutions: dict) -> Any:
        if isinstance(node, list):
            return [self.substitute(x, substitutions) for x in node]
        if not isinstance(node, dict):
            return deepcopy(node)
        if set(node) == {"var"}:
            return deepcopy(substitutions.get(node["var"], node))
        if node.get("op") in {"exists", "forall", "lambda"}:
            key = "parameters" if node["op"] == "lambda" else "variables"
            if not isinstance(node.get(key), list):
                raise ValueError("INVALID_BINDER: provider binder is malformed")
            result = deepcopy(node)
            local = dict(substitutions)
            result[key] = []
            for parameter in node[key]:
                if not isinstance(parameter, dict) or not isinstance(parameter.get("name"), str):
                    raise ValueError("INVALID_BINDER: provider binder is malformed")
                old = parameter["name"]
                new = self.fresh(old)
                local[old] = {"var": new}
                result[key].append({**parameter, "name": new})
            result["body"] = self.substitute(node.get("body"), local)
            return result
        return {k: self.substitute(v, substitutions) if isinstance(v, (dict, list)) else deepcopy(v) for k, v in node.items()}

    def instantiate(self, call: dict, side: str, round_number: int):
        record = _provider(call, self.context, round_number)
        parameters = record["parameters"]
        args = call.get("args")
        if not isinstance(args, list) or len(args) != len(parameters):
            raise ValueError("CALL_ARITY_MISMATCH: cannot instantiate a partial usage")
        names = [p.get("name") for p in parameters if isinstance(p, dict)]
        if len(names) != len(parameters) or not all(isinstance(n, str) for n in names) or len(set(names)) != len(names):
            raise ValueError("PROVIDER_INCOMPLETE: invalid parameter declarations")
        free = _free(record[side])
        if free - set(names):
            raise ValueError("PROVIDER_UNBOUND_VARIABLE: provider contains undeclared free variables")
        for node in _walk(record[side]):
            if node.get("op") == "primitive" and "origin" in node:
                raise ValueError("FORGED_PRIMITIVE_ORIGIN: provider AST cannot claim expansion provenance")
            key = "parameters" if node.get("op") == "lambda" else "variables"
            if node.get("op") in {"lambda", "exists", "forall"}:
                if any(p.get("name") in names for p in node.get(key, []) if isinstance(p, dict)):
                    raise ValueError("EXTERNAL_PARAMETER_CAPTURE: provider rebinds an external input")
        body = self.substitute(record[side], dict(zip(names, args)))
        if side == "lhs":
            targets = [node for node in _walk(body) if node.get("op") == "target"]
            if len(targets) != 1:
                raise ValueError("PROVIDER_INCOMPLETE: provider LHS lacks one target")
            targets[0]["synset_id"] = record["synset_id"]
            targets[0]["usage_id"] = record["usage_id"]
        return body, record

    def expand(self, node: Any, owner: dict, round_number: int, stack: tuple = ()) -> Any:
        if isinstance(node, list):
            return [self.expand(x, owner, round_number, stack) for x in node]
        if not isinstance(node, dict):
            return deepcopy(node)
        if node.get("op") == "use":
            key = provider_key(node.get("synset_id", ""), node.get("usage_id", ""))
            if key in stack:
                raise ValueError(f"PROVIDER_CYCLE: {key}")
            # Expand caller-owned arguments before substituting into a provider.
            call = deepcopy(node)
            call["args"] = self.expand(call.get("args"), owner, round_number, stack)
            body, record = self.instantiate(call, "rhs", round_number)
            return self.expand(body, record, record["round"], (*stack, key))
        result = {k: self.expand(v, owner, round_number, stack) if isinstance(v, (dict, list)) else deepcopy(v) for k, v in node.items()}
        if node.get("op") == "primitive":
            # Already expanded caller arguments retain their original provenance.
            if "origin" in node:
                origin = node["origin"]
                if not isinstance(origin, dict) or origin.get("synset_id") not in self.context.get("basis_ids", []):
                    raise ValueError("NONBASIS_PRIMITIVE: invalid expanded primitive origin")
                return deepcopy(node)
            if owner.get("synset_id") not in self.context.get("basis_ids", []):
                raise ValueError("NONBASIS_PRIMITIVE: expanded primitive has no basis owner")
            declarations = {p.get("name"): p for p in owner.get("primitives", []) if isinstance(p, dict)}
            if node.get("name") not in declarations:
                raise ValueError("UNDECLARED_PRIMITIVE: expanded primitive is absent from its basis declaration")
            origin = {"synset_id": owner["synset_id"], "usage_id": owner["usage_id"], "provider_hash": owner.get("bundle_hash") or canonical_hash(owner)}
            result["declared_name"] = node["name"]
            result["name"] = f"{origin['synset_id']}@{origin['provider_hash']}::{node['name']}"
            result["origin"] = origin
        return result


def instantiate_provider_call(call: dict, context: dict, side: str = "lhs") -> dict:
    """Instantiate a complete approved pattern, with hygienic local bindings.

    This is useful for displaying what a ``use`` macro actually denotes.  It
    never emits a new logical USE predicate or a bare target dependency call.
    """
    if side not in {"lhs", "rhs"}:
        raise ValueError("side must be lhs or rhs")
    expander = _Expander(context, call)
    return expander.instantiate(call, side, context.get("round", 0))[0]


def expand_formula(candidate: dict, context: dict, side: str = "rhs") -> dict:
    """Recursively expand certified usage definitions without variable capture.

    Call validate_formula first: expansion is not a substitute for local gates
    or semantic review.  Unresolved, stale, circular and opaque calls fail.
    """
    if side not in {"lhs", "rhs"} or not isinstance(candidate.get(side), dict):
        raise ValueError("side must identify a formula AST")
    # Authored input cannot forge an expansion-origin annotation.
    if any("origin" in n and n.get("op") == "primitive" for n in _walk(candidate.get(side))):
        raise ValueError("FORGED_PRIMITIVE_ORIGIN: authored AST cannot claim expansion provenance")
    return _Expander(context, candidate).expand(candidate[side], candidate, context.get("round", 0))
