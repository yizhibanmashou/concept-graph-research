"""Validate a finite supplied-formula search problem without interpreting prose.

This module reads V3 identities and AST contracts, never published/legacy formula
registries. Providers are explicit assumptions, not newly certified definitions.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from .common import canonical_hash, project_root, read_json
from .gates import validate_source
from .parameter_projection import prepare_parameter_projection
from .nominalization import RESERVED, prepare_nominalizations, nominal_options
from .event_closure import prepare_event_bindings


BASE_TYPES = {"E", "V", "Time", "World", "Prop"}
RELATIONS = {"Agent", "Theme", "Happen"}
VARIABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
OEWN_ID = re.compile(r"^oewn-\d{8}-([nvars])$")
POS_ALIASES = {"n": "n", "noun": "n", "v": "v", "verb": "v", "a": "a",
               "s": "a", "adjective": "a", "adjective_satellite": "a", "r": "r", "adverb": "r"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _keys(value: Any, allowed: set[str], where: str) -> dict:
    _require(isinstance(value, dict), f"{where} must be an object")
    _require(not set(value) - allowed,
             f"Unsupported {where} field(s): {sorted(set(value) - allowed)}")
    return value


def _list(value: Any, where: str) -> list:
    _require(isinstance(value, list), f"{where} must be a list")
    return value


def _type(value: Any) -> bool:
    if isinstance(value, str):
        return value in BASE_TYPES
    return (isinstance(value, dict) and set(value) == {"arrow"}
            and isinstance(value["arrow"], list) and len(value["arrow"]) >= 2
            and all(_type(t) for t in value["arrow"]))


def _parameters(rows: Any, where: str, *, roles: bool = True) -> dict:
    names = {}
    for row in _list(rows, where):
        _require(isinstance(row, dict) and isinstance(row.get("name"), str)
                 and VARIABLE_NAME.fullmatch(row["name"]) is not None and _type(row.get("type")),
                 f"{where} entries need a name and finite V3 type")
        _require(not set(row) - {"name", "type", "role"}, f"Unsupported V3 parameter fields in {where}")
        _require(row["name"] not in names, f"Duplicate variable in {where}: {row['name']}")
        if roles:
            _require(_text(row.get("role")), f"{where} entries need an explicit role")
        names[row["name"]] = row["type"]
    return names


def _pos(occurrence: dict, pos: str) -> bool:
    supplied = occurrence.get("pos", occurrence.get("part_of_speech"))
    aliases = {"n": {"n", "noun"}, "v": {"v", "verb"}}
    return supplied in aliases[pos] or occurrence["synset_id"].endswith("-" + pos)


def _plan_term(value: Any) -> dict:
    return {"var": value} if isinstance(value, str) else {
        "op": "struct", "name": "ImplicitSubj", "args": [{"var": value["implicit_subject"]}]}


def _atom(row: dict) -> dict:
    return {"op": "struct", "name": row["name"], "args": [_plan_term(a) for a in row["arguments"]]}


def _conjunction(nodes: list[dict]) -> dict:
    return nodes[0] if len(nodes) == 1 else {"op": "and", "args": nodes}


def _validate_provider_formulas(providers: dict, structures: dict, *, interface_only: bool = False) -> None:
    """Check that assumed formulas are complete typed ASTs, without certifying meaning."""
    signatures = {key: [p["type"] for p in row["parameters"]] for key, row in providers.items()}
    for key, provider in providers.items():
        primitive_types = {}
        for item in _list(provider.get("primitives", []), f"{key}.primitives"):
            _require(isinstance(item, dict) and item.get("name") not in RESERVED,
                     "NominalRef/Holds are reserved for Nom expansion, not provider primitives")
            _require(isinstance(item, dict) and _text(item.get("name"))
                     and isinstance(item.get("argument_types"), list)
                     and all(_type(t) for t in item["argument_types"])
                     and _type(item.get("return_type"))
                     and _text(item.get("meaning")) and _text(item.get("source_evidence")),
                     f"Incomplete primitive declaration in provider {key}")
            _require(item["name"] not in primitive_types, f"Duplicate primitive in {key}")
            primitive_types[item["name"]] = (item["argument_types"], item["return_type"])
        _require(provider["is_basis"] or not primitive_types,
                 f"Nonbasis provider {key} cannot introduce primitive declarations")
        target_count = 0

        def infer(node: Any, env: dict, side: str) -> Any:
            nonlocal target_count
            _require(isinstance(node, dict) and bool(node), f"Incomplete formula AST in {key}")
            if "var" in node:
                _require(set(node) == {"var"} and isinstance(node["var"], str) and node["var"] in env,
                         f"Unknown variable in provider {key}")
                return env[node["var"]]
            op = node.get("op")
            _require(isinstance(op, str), f"Missing formula operation in provider {key}")
            if interface_only:
                _require(op in {"target", "and", "struct"},
                         f"Interface {key} LHS may contain only target, AND and allowed structures")
                allowed = {"op", "args", "name"} if op == "struct" else {"op", "args"}
                _require(not set(node) - allowed, f"Unsupported interface LHS fields in {key}")
                if op == "target":
                    _require(all(isinstance(a, dict) and set(a) == {"var"} for a in node.get("args", [])),
                             "Interface target arguments must be declared parameters")
                if op == "struct":
                    _require(node.get("name") in RELATIONS | {"ImplicitSubj"},
                             "Interface LHS cannot introduce a world term or a new structure")
            if op in {"target", "primitive", "struct", "use", "apply"}:
                args = _list(node.get("args"), f"{key}.{op}.args")
                if op == "target":
                    _require(side == "lhs", f"Provider {key} has target on RHS")
                    target_count += 1
                    for arg in args:
                        infer(arg, env, side)
                    return "Prop"
                if op == "primitive":
                    _require(provider["is_basis"] and node.get("name") in primitive_types,
                             f"Unknown/unauthorized provider primitive in {key}")
                    expected, result = primitive_types[node["name"]]
                elif op == "struct":
                    relation = structures.get("relations", {}).get(node.get("name"))
                    _require(isinstance(relation, dict), f"Unknown provider structure in {key}")
                    expected, result = relation["argument_types"], relation["return_type"]
                elif op == "use":
                    dependency = str(node.get("synset_id")) + "::" + str(node.get("usage_id"))
                    _require(dependency in signatures, f"Provider {key} has missing transitive formula {dependency}")
                    _require(node.get("provider_hash") == providers[dependency]["bundle_hash"],
                             f"Provider {key} has a stale transitive provider hash")
                    _require(providers[dependency]["round"] < provider["round"],
                             f"Provider {key} has non-earlier or recursive dependency {dependency}")
                    expected, result = signatures[dependency], "Prop"
                else:
                    function = infer(node.get("function"), env, side)
                    _require(isinstance(function, dict) and "arrow" in function,
                             f"Provider {key} applies a non-function")
                    expected, result = function["arrow"][:-1], function["arrow"][-1]
                _require(len(args) == len(expected), f"Provider {key} has wrong call arity")
                for arg, wanted in zip(args, expected):
                    actual = infer(arg, env, side)
                    _require(actual in wanted if isinstance(wanted, list) else actual == wanted,
                             f"Provider {key} has an ill-typed argument")
                return result
            if op in {"and", "or"}:
                args = _list(node.get("args"), f"{key}.{op}.args")
                _require(len(args) >= 2, f"Provider {key} has empty/unary connective")
                _require(all(infer(a, env, side) == "Prop" for a in args), f"Non-proposition connective in {key}")
                return "Prop"
            if op == "not":
                _require(infer(node.get("body"), env, side) == "Prop", f"Non-proposition negation in {key}")
                return "Prop"
            if op == "at_world":
                _require(provider["is_basis"], "World evaluation syntax may only originate in a supplied basis definition")
                _require(infer(node.get("world"), env, side) == "World", "World evaluation needs a typed world")
                _require(infer(node.get("body"), env, side) == "Prop", "World evaluation needs a full proposition")
                return "Prop"
            if op in {"implies", "iff", "eq"}:
                left = infer(node.get("left"), env, side)
                right = infer(node.get("right"), env, side)
                _require(left == right and (op == "eq" or left == "Prop"), f"Ill-typed connective in {key}")
                return "Prop"
            if op in {"lambda", "exists", "forall"}:
                field = "parameters" if op == "lambda" else "variables"
                local = _parameters(node.get(field), f"{key}.{field}", roles=False)
                _require(bool(local) and not set(local) & set(env), f"Empty/capturing binder in provider {key}")
                body = infer(node.get("body"), {**env, **local}, side)
                if op == "lambda":
                    return {"arrow": list(local.values()) + [body]}
                _require(body == "Prop", f"Non-proposition quantified body in {key}")
                return "Prop"
            raise ValueError(f"Unsupported/incomplete provider AST operation {op!r} in {key}")

        env = {p["name"]: p["type"] for p in provider["parameters"]}
        _require(infer(provider.get("lhs"), env, "lhs") == "Prop" and target_count == 1,
                 f"Provider {key} needs a complete LHS with exactly one target")
        if interface_only:
            def check_lhs(node, parent=None, index=None):
                if "var" in node:
                    return {node["var"]}
                if node.get("name") == "ImplicitSubj":
                    _require(provider.get("voice") == "passive" and parent is not None
                             and parent.get("name") == "Agent" and index == 1
                             and node["args"] == [parent["args"][0]],
                             "ImplicitSubj requires passive Agent(e,ImplicitSubj(e))")
                names = set()
                for i, arg in enumerate(node.get("args", [])):
                    names.update(check_lhs(arg, node, i))
                return names
            _require(set(env) <= check_lhs(provider["lhs"]),
                     f"Interface {key} LHS must retain every parameter")
        else:
            _require(infer(provider.get("rhs"), env, "rhs") == "Prop", f"Provider {key} needs a complete RHS")


def _prepare_request(request: dict, project: str | Path | None = None) -> dict:
    """Return a finite normalized search contract; invalid/unsupported input raises.

    No returned flag is a usage or semantic certification. Argumentation text is
    retained verbatim and only explicit structured constraints prune the search.
    """
    interface_only = request.get("schema_version") == "v3.enumeration-interfaces-input/1"
    _keys(request, {"schema_version", "source", "usage", "interfaces" if interface_only else "providers",
                    "enumeration", "notice"} | ({"interface_assumptions"} if interface_only else set()), "request")
    _require(interface_only or request.get("schema_version") == "v3.enumeration-input/1",
             "Expected v3.enumeration-input/1 or v3.enumeration-interfaces-input/1")
    original = deepcopy(request)
    project = Path(project) if project is not None else project_root()
    policy = read_json(project / "config/policy.json")
    structures = read_json(project / "config/structural_relations.json")
    frozen_basis = read_json(project / "sources/basis_ids.json")["basis_ids"]
    source = deepcopy(request.get("source"))
    _require(isinstance(source, dict) and source.get("is_basis") is False,
             "Enumeration target must be a nonbasis V3 source")
    source_issues = validate_source(source, {"basis_ids": frozen_basis})
    _require(not source_issues, "Invalid fixed source/WSD: " + repr(source_issues))
    _require(isinstance(source.get("lemmas"), list) and all(_text(x) for x in source["lemmas"])
             and isinstance(source.get("evidence"), list) and isinstance(source.get("provenance"), dict),
             "Source needs V3 lemmas, evidence and provenance")
    occurrences = {row["occurrence_id"]: row for row in source["occurrences"]}
    _require(len({(row["start"], row["end"]) for row in occurrences.values()}) == len(occurrences),
             "A source span cannot be duplicated to inflate occurrence budgets")
    for row in occurrences.values():
        declared = [POS_ALIASES.get(row[field], row[field]) for field in ("pos", "part_of_speech") if field in row]
        _require(all(_text(kind) for kind in declared) and len(set(declared)) <= 1,
                 "Conflicting source POS declarations")
        identity_pos = OEWN_ID.fullmatch(row["synset_id"])
        if identity_pos and declared:
            authoritative = POS_ALIASES[identity_pos[1]]
            if authoritative in {"n", "v"} or declared[0] in {"n", "v"}:
                _require(declared[0] == authoritative, "Declared POS conflicts with frozen OEWN identity")
        if row["synset_id"].startswith("@syntax:"):
            _require(row["synset_id"] in {"@syntax:a", "@syntax:the"}, "Unsupported syntax occurrence")
            expected = {"a", "an"} if row["synset_id"] == "@syntax:a" else {"the"}
            _require(row["text"].casefold() in expected, "Article identity and original text disagree")

    # Missing function-word WSD can be investigated under a separately supplied
    # user contract. This is an occurrence-local research assumption, never a
    # repaired frozen identity or an extension of the published Basis85 set.
    interface_assumptions = {}
    for assumption in _list(request.get("interface_assumptions", []), "interface_assumptions"):
        _keys(assumption, {"synset_id", "occurrence_ids", "reason", "authorization"}, "interface assumption")
        sid, ids = assumption.get("synset_id"), assumption.get("occurrence_ids")
        _require(_text(sid) and sid not in frozen_basis and sid != source["synset_id"]
                 and not sid.startswith("@syntax:") and sid not in interface_assumptions,
                 "An interface assumption must name one distinct nonpublished lexical identity")
        _require(isinstance(ids, list) and bool(ids) and all(isinstance(oid, str) for oid in ids)
                 and len(ids) == len(set(ids))
                 and set(ids) == {oid for oid, row in occurrences.items() if row["synset_id"] == sid},
                 "Interface assumption must identify exactly its supplied source occurrences")
        _require(_text(assumption.get("reason")) and _text(assumption.get("authorization")),
                 "Interface assumption requires its reason and explicit authorization provenance")
        for oid in ids:
            occurrence = occurrences[oid]
            for field in ("frozen_synset_id", "original_synset_id"):
                _require(field not in occurrence or occurrence[field] in (None, sid),
                         "An interface assumption cannot override an existing frozen WSD identity")
        interface_assumptions[sid] = deepcopy(assumption)

    usage = deepcopy(request.get("usage"))
    _require(isinstance(usage, dict) and _text(usage.get("usage_id")), "One V3 usage is required")
    for field in ("sentence_a", "sentence_b", "argumentation"):
        _require(_text(usage.get(field)), f"usage.{field} is required")
    for field in ("evidence", "reductions"):
        _require(isinstance(usage.get(field), list) and all(_text(x) for x in usage[field]),
                 f"usage.{field} must contain textual records")
    _require(bool(usage["evidence"]), "Usage needs evidence")
    external = _parameters(usage.get("parameters"), "usage.parameters")
    targets = _list(usage.get("target_arguments"), "usage.target_arguments")
    _require(all(isinstance(name, str) and name in external for name in targets), "Target arguments must be external parameters")
    used_source = _list(usage.get("occurrence_ids"), "usage.occurrence_ids")
    _require(all(isinstance(x, str) and x in occurrences for x in used_source)
             and len(set(used_source)) == len(used_source), "Usage contains unknown/duplicate occurrence identity")
    _require(usage.get("voice") in {"active", "passive"}, "Usage voice must be active or passive")
    projection = prepare_parameter_projection(source, usage)
    parameter_ids = set(projection["parameter_occurrence_ids"])
    parameter_determiners = set(projection["covered_determiner_ids"])
    enum = deepcopy(request.get("enumeration", {}))
    _keys(enum, {"lexical", "noun_licenses", "verb_occurrence_ids", "structural_budgets",
                 "required_structures", "slot_scopes", "lhs_structures", "quantifier_inventory_complete",
                 "event_structure_licenses", "scope_templates", "nominalizations", "event_bindings"}, "enumeration")
    if "quantifier_inventory_complete" in enum:
        _require(enum["quantifier_inventory_complete"] is True, "Quantifier inventory must be explicitly complete when supplied")

    providers = deepcopy(request.get("interfaces" if interface_only else "providers"))
    _require(isinstance(providers, dict), "providers must map exact synset::usage identities to formulas")
    for key, provider in providers.items():
        _require(isinstance(provider, dict) and _text(provider.get("synset_id")) and _text(provider.get("usage_id")),
                 "Provider requires exact synset and usage identities")
        _require(key == provider["synset_id"] + "::" + provider["usage_id"], "Provider key/identity mismatch")
        _require(provider["synset_id"] != source["synset_id"], "The unknown target cannot provide its own formula")
        _parameters(provider.get("parameters"), f"providers.{key}.parameters")
        _require(type(provider.get("is_basis")) is bool, f"Provider {key} needs its supplied basis flag")
        if interface_only:
            _keys(provider, {"synset_id", "usage_id", "is_basis", "parameters", "lhs", "rhs_status",
                             "interface_hash", "evidence", "description", "usage_description", "voice"},
                  f"interfaces.{key}")
            is_frozen = provider["synset_id"] in frozen_basis
            assumption = interface_assumptions.get(provider["synset_id"])
            _require((is_frozen and provider["is_basis"]) or
                     (assumption is not None and provider["is_basis"] is False),
                     "LHS-only interfaces need a frozen Basis85 identity or an explicit occurrence-local assumption")
            _require(provider.get("rhs_status") == "pending", "Interface RHS status must be pending")
            if "voice" in provider:
                _require(provider["voice"] in {"active", "passive"}, "Invalid interface voice")
            hash_payload = {field: provider.get(field) for field in
                            ("synset_id", "usage_id", "is_basis", "parameters", "lhs", "voice")}
            if assumption is not None:
                hash_payload["interface_assumption"] = assumption
            digest = canonical_hash(hash_payload)
            _require("interface_hash" not in provider or provider["interface_hash"] == digest,
                     "Interface hash does not match its identity, typed parameters and LHS")
            provider["interface_hash"] = digest
            continue
        _require(type(provider.get("round", 0)) is int and provider.get("round", 0) >= 0, "Invalid provider round")
        provider.setdefault("round", 0)
        if "bundle_hash" not in provider:
            provider["bundle_hash"] = canonical_hash(provider)
        _require(_text(provider["bundle_hash"]), "Provider snapshot hash must be textual")
        provider.setdefault("primitives", [])
        # This copy is for legacy gate annotations only; the original snapshot
        # and its hash remain available in original_request.
        provider["mode"] = "demo"
    _require(set(interface_assumptions) <= {p["synset_id"] for p in providers.values()},
             "Unused interface assumption has no supplied LHS")
    _validate_provider_formulas(providers, structures, interface_only=interface_only)
    nominalizations, nominalization_analysis = prepare_nominalizations(
        source, usage, enum, providers, interface_only=interface_only,
        policy=read_json(project / "config/nominalization.json") if enum.get("nominalizations") else {})
    nominal_by_head = {row["head_occurrence_id"]: row for row in nominalizations.values()}
    _require(not set(nominal_by_head) & parameter_ids,
             "A parameter-only phrase cannot also supply Nom lexical content")

    def nominal_head(oid):
        return oid in occurrences and (_pos(occurrences[oid], "n") or oid in nominal_by_head)

    fixed = deepcopy(usage.get("binding_plan"))
    if fixed is not None:
        _keys(fixed, {"lexical", "structural", "scopes"}, "usage.binding_plan")
        _list(fixed.get("lexical"), "binding_plan.lexical")
        _keys(fixed.get("structural"), {"lhs", "rhs"}, "binding_plan.structural")
        for side in ("lhs", "rhs"):
            _list(fixed["structural"].get(side), "binding_plan.structural." + side)
    scopes = deepcopy(fixed.get("scopes", [])) if fixed is not None else []
    if "scope_templates" in enum:
        _require(fixed is None or "scopes" not in fixed or enum["scope_templates"] == scopes,
                 "Enumeration scope templates conflict with the fixed binding plan")
        scopes = deepcopy(enum["scope_templates"])
    scope_ids, local_types, local_choices = set(), {}, {}
    for scope in _list(scopes, "binding_plan.scopes"):
        _keys(scope, {"scope_id", "parent_scope", "kind", "variables"}, "scope")
        _require(_text(scope.get("scope_id")) and scope["scope_id"] not in scope_ids
                 and scope.get("kind") == "lambda", "Only unique fixed lambda scopes are supported")
        _require(scope.get("parent_scope") is None or _text(scope["parent_scope"]), "Invalid parent_scope")
        local = _parameters(scope.get("variables"), "scope.variables", roles=False)
        _require(bool(local) and not set(local) & set(external), "Scope locals cannot capture external variables")
        for name, kind in local.items():
            if kind not in local_choices.setdefault(name, []):
                local_choices[name].append(kind)
        local_types.update(local)
        scope_ids.add(scope["scope_id"])
    scope_by_id = {row["scope_id"]: row for row in scopes}
    for sid in scope_ids:
        ancestor, seen = sid, set()
        while ancestor is not None:
            _require(ancestor in scope_by_id and ancestor not in seen, "Unknown/cyclic parent_scope")
            seen.add(ancestor)
            ancestor = scope_by_id[ancestor]["parent_scope"]
        ancestors = seen - {sid}
        inherited_names = {p["name"] for ancestor in ancestors for p in scope_by_id[ancestor]["variables"]}
        _require(not inherited_names & {p["name"] for p in scope_by_id[sid]["variables"]},
                 "Lambda locals cannot shadow ancestor locals")

    determiners = _list(usage.get("determiners"), "usage.determiners")
    determiner_by_id = {}
    for row in determiners:
        _require(isinstance(row, dict) and row.get("occurrence_id") in occurrences,
                 "Determiner needs its frozen occurrence")
        oid = row["occurrence_id"]
        if oid in parameter_determiners:
            continue
        _require(oid not in determiner_by_id, "Duplicate determiner analysis")
        surface = occurrences[oid]["text"].casefold()
        _require(row.get("kind") in {"a", "the", "all"}
                 and surface in ({"a", "an"} if row["kind"] == "a" else {row["kind"]}),
                 "Determiner kind does not match source")
        if row["kind"] == "all":
            _require(row.get("action") == "provider" and not occurrences[oid]["synset_id"].startswith("@syntax:"),
                     "Nonbasis all must call its fixed lexical provider")
        else:
            head = row.get("head_occurrence_id")
            _require(nominal_head(head), "Determiner needs an actual nominal head")
            _require(row.get("action") in ({"parameter", "exists"} if row["kind"] == "a" else {"share", "drop"}),
                     "Invalid determiner action")
            if row["action"] != "exists":
                scoped = (row["kind"] == "the" and row.get("scope_id") in scope_by_id
                          and any(p["name"] == row.get("parameter") for p in scope_by_id[row["scope_id"]]["variables"]))
                _require(row.get("parameter") in external or scoped,
                         "a parameter/the must retain its external or explicitly operator-bound parameter")
            if row["action"] == "share":
                _require(row.get("antecedent") == row.get("parameter"), "the sharing must use the antecedent parameter")
        determiner_by_id[oid] = row
    exclusions = usage.get("determiner_exclusions", [])
    excluded_ids = set()
    for row in _list(exclusions, "usage.determiner_exclusions"):
        _require(isinstance(row, dict) and row.get("occurrence_id") in occurrences and _text(row.get("reason")),
                 "Determiner exclusion requires source identity and reason")
        _require(row["occurrence_id"] not in determiner_by_id and row["occurrence_id"] not in excluded_ids,
                 "Duplicate/contradictory determiner exclusion")
        excluded_ids.add(row["occurrence_id"])
    for oid, row in occurrences.items():
        if row["text"].casefold() in {"a", "an", "the", "all"}:
            _require(oid in determiner_by_id or oid in excluded_ids or oid in parameter_determiners,
                     "Every source determiner needs explicit analysis/exclusion or parameter-span disposition")

    licenses, witness_by_name, head_owner = [], {}, {}

    def add_witness(name, type_, origin, oid, head, required, reason):
        _require(isinstance(name, str) and VARIABLE_NAME.fullmatch(name) is not None,
                 "Witness name must be a valid V3 variable identifier")
        _require(name not in external and name not in local_types, "Witness captures an external/local parameter")
        _require(_type(type_), "Nominal witnesses need a supplied finite V3 type")
        _require(nominal_head(head), "Witness needs a fixed nominal source head")
        _require(head not in nominal_by_head or type_ == "E",
                 "A nominalized verb licenses an E referent, never an ordinary V event witness")
        _require(type_ != "V", "A noun witness cannot introduce V; use an occurrence-owned verb_event license")
        _require(type(required) is bool and _text(reason), "Witness requires boolean required and textual reason")
        witness = {"name": name, "type": type_, "origin": origin, "occurrence_id": oid,
                   "head_occurrence_id": head, "required": required, "reason": reason}
        if name in witness_by_name:
            old = witness_by_name[name]
            _require(all(old[field] == witness[field] for field in ("type", "origin", "occurrence_id", "head_occurrence_id")),
                     "Conflicting witness declarations")
            old["required"] = old["required"] or required
            return old
        _require(head not in head_owner, "A noun occurrence cannot license a second witness")
        head_owner[head] = name
        witness_by_name[name] = witness
        return witness

    seen_licenses = set()
    for license_ in _list(enum.get("noun_licenses", []), "enumeration.noun_licenses"):
        _keys(license_, {"occurrence_id", "origin", "article_occurrence_id", "name", "type", "required", "reason"}, "noun_license")
        head, origin = license_.get("occurrence_id"), license_.get("origin")
        _require(head not in parameter_ids and license_.get("article_occurrence_id") not in parameter_ids,
                 "A parameter phrase cannot license an internal witness")
        _require(nominal_head(head), "Noun license must identify a nominal occurrence")
        _require(head not in seen_licenses, "Only one explicit license per noun occurrence")
        seen_licenses.add(head)
        _require(origin in {"a", "bare_mass", "nominalization"}, "Unlicensed nominal witness origin")
        if origin == "nominalization":
            _require(head in nominal_by_head and license_.get("type") == "E",
                     "A Nom witness requires a validated nominalized verb and has type E")
        elif origin == "bare_mass":
            _require(head not in nominal_by_head,
                     "A nominalized verb uses its explicit nominalization license, not a guessed mass-noun WSD")
        oid = head
        if origin == "a":
            oid = license_.get("article_occurrence_id")
            _require(oid in occurrences and occurrences[oid]["text"].casefold() in {"a", "an"},
                     "a license requires a/an in the definition")
            analysis = determiner_by_id.get(oid)
            _require(analysis is not None and analysis.get("action") == "exists"
                     and analysis.get("head_occurrence_id") == head, "a license must match determiner argumentation")
            if analysis.get("parameter") is not None:
                _require(analysis["parameter"] == license_.get("name"), "a witness disagrees with determiner parameter")
        else:
            _require("article_occurrence_id" not in license_, "Bare mass license cannot cite an article")
            _require(not any(row.get("head_occurrence_id") == head for row in determiners),
                     "Bare mass witness cannot reinterpret an article-qualified noun")
        add_witness(license_.get("name"), license_.get("type"),
                    "a" if origin == "a" else "nominalization" if origin == "nominalization" else "definition_internal",
                    oid, head, license_.get("required", False), license_.get("reason"))
        licenses.append(license_)
    for witness in _list(usage.get("witnesses", []), "usage.witnesses"):
        _require(isinstance(witness, dict), "Witness must be an object")
        origin, oid = witness.get("origin"), witness.get("occurrence_id")
        _require(origin in {"a", "definition_internal", "nominalization"}, "Unlicensed existential origin")
        if origin == "a":
            analysis = determiner_by_id.get(oid)
            _require(analysis is not None and analysis.get("action") == "exists", "Witness a must match determiner analysis")
            head = analysis["head_occurrence_id"]
        elif origin == "nominalization":
            _require(oid in nominal_by_head and witness.get("type") == "E"
                     and any(row["origin"] == "nominalization" and row.get("name") == witness.get("name")
                             and row["occurrence_id"] == oid for row in licenses),
                     "Nom witness needs its explicit construction/noun license")
            head = oid
        else:
            matches = [row for row in licenses if row["origin"] == "bare_mass" and row.get("name") == witness.get("name")
                       and row["occurrence_id"] == oid]
            _require(matches or (oid in occurrences and _pos(occurrences[oid], "n")
                     and occurrences[oid].get("countability") in {"mass", "uncountable", "bare_mass"}),
                     "definition_internal requires explicit bare-mass licensing, not an arbitrary internal cause")
            head = oid
        add_witness(witness.get("name"), witness.get("type"), origin, oid, head, True, witness.get("reason"))
    event_bindings, event_witnesses = prepare_event_bindings(
        source, usage, enum, providers, nominalizations, nominalization_analysis, scope_by_id,
        parameter_ids, excluded_ids, witness_by_name, interface_only=interface_only,
        policy=read_json(project / "config/event_closure.json") if enum.get("event_bindings") else {})
    for witness in event_witnesses:
        witness_by_name[witness["name"]] = witness
    head_bindings = {}
    required_occurrences = set()
    for oid, row in determiner_by_id.items():
        required_occurrences.add(oid)
        if row["kind"] == "all":
            continue
        head = row["head_occurrence_id"]
        required_occurrences.add(head)
        if row["action"] == "exists":
            matching = [w for w in witness_by_name.values() if w["origin"] == "a" and w["occurrence_id"] == oid]
            _require(len(matching) == 1, "a exists must supply exactly one licensed internal witness")
            matching[0]["required"] = True
            name = matching[0]["name"]
        else:
            name = row["parameter"]
        head_bindings.setdefault(head, []).append(name)
    for witness in witness_by_name.values():
        if witness["required"]:
            required_occurrences.add(witness["head_occurrence_id"])
        # Optional witnesses enforce their nominal head when selected in search.
    all_types = {**external, **local_types, **{n: w["type"] for n, w in witness_by_name.items()}}

    def variable_types(name, scope_id=None, *, lhs=False):
        if name in external:
            return [external[name]]
        if lhs:
            return []
        if name in witness_by_name:
            return [witness_by_name[name]["type"]]
        if scope_id is not None:
            while scope_id is not None:
                scope = scope_by_id[scope_id]
                for variable in scope["variables"]:
                    if variable["name"] == name:
                        return [variable["type"]]
                scope_id = scope["parent_scope"]
            return []
        return local_choices.get(name, [])

    overrides = {}
    for row in _list(enum.get("lexical", []), "enumeration.lexical"):
        _keys(row, {"occurrence_id", "min_calls", "max_calls", "usage_ids", "bindings"}, "lexical resource")
        oid = row.get("occurrence_id")
        _require(oid not in parameter_ids, "A parameter phrase cannot supply an enumerated lexical call")
        _require(oid in occurrences and oid not in overrides and not occurrences[oid]["synset_id"].startswith("@syntax:"),
                 "Lexical override must identify one distinct callable occurrence")
        overrides[oid] = row
    fixed_by_occurrence = {}
    if fixed is not None:
        for row in fixed["lexical"]:
            _keys(row, {"occurrence_id", "usage_id", "bindings", "scope_id"}, "fixed lexical binding")
            oid = row.get("occurrence_id")
            _require(oid in occurrences and oid not in fixed_by_occurrence and oid in used_source,
                     "Fixed plan needs distinct in-usage occurrence resources")
            _require(_text(row.get("usage_id")), "Fixed lexical plan needs usage_id")
            _require(row.get("scope_id") is None or row["scope_id"] in scope_ids, "Unknown fixed binding scope")
            fixed_by_occurrence[oid] = row
            required_occurrences.add(oid)

    lexical = []
    for oid, occurrence in occurrences.items():
        if occurrence["synset_id"].startswith("@syntax:") or oid in parameter_ids:
            continue
        override = overrides.get(oid, {})
        minimum, maximum = override.get("min_calls", 0), override.get("max_calls", 1)
        _require(type(minimum) is int and type(maximum) is int and 0 <= minimum <= maximum <= 1,
                 "Each definition occurrence supplies at most one lexical call")
        if oid not in used_source or oid in excluded_ids:
            _require(minimum == 0 and oid not in required_occurrences, "Excluded/out-of-usage occurrence cannot be required")
            maximum = 0
        if fixed is not None and oid not in fixed_by_occurrence:
            _require(minimum == 0 and oid not in required_occurrences,
                     "Frozen binding_plan omits an explicitly required lexical occurrence")
            maximum = 0
        if oid in required_occurrences:
            _require(maximum == 1, "Required argumentation occurrence cannot have max_calls=0")
            minimum = 1
        options = [p for p in providers.values() if p["synset_id"] == occurrence["synset_id"]]
        _require(bool(options), f"Missing supplied provider for fixed-WSD occurrence {oid}")
        selected = override.get("usage_ids")
        if selected is not None:
            _require(isinstance(selected, list) and selected and all(_text(x) for x in selected)
                     and len(set(selected)) == len(selected), "usage_ids must be nonempty distinct known usages")
            _require(set(selected) <= {p["usage_id"] for p in options}, "Unknown selected provider usage")
            options = [p for p in options if p["usage_id"] in selected]
        if oid in fixed_by_occurrence:
            uid = fixed_by_occurrence[oid]["usage_id"]
            _require(uid in {p["usage_id"] for p in options}, "Fixed usage conflicts with selected providers")
            options = [p for p in options if p["usage_id"] == uid]
        if oid in event_bindings:
            uid = event_bindings[oid]["usage_id"]
            _require(uid in {p["usage_id"] for p in options}, "Event ownership conflicts with selected verb usage")
            options = [p for p in options if p["usage_id"] == uid]
        normalized_options = []
        for provider in sorted(options, key=lambda row: row["usage_id"]):
            for parameter in provider["parameters"]:
                kind = parameter["type"]
                _require(not isinstance(kind, dict) or kind["arrow"][-1] == "Prop",
                         "Unsupported generated function slot: return type must be Prop")
            bindings = deepcopy(override.get("bindings", {}))
            _require(isinstance(bindings, dict), "Lexical bindings must be an object")
            known = fixed_by_occurrence.get(oid, {}).get("bindings", {})
            _require(isinstance(known, dict), "Fixed lexical bindings must be an object")
            for name, variable in known.items():
                _require(name not in bindings or bindings[name] == variable, "Enumeration conflicts with certified lexical binding")
                bindings[name] = variable
            if oid in event_bindings:
                event_binding = event_bindings[oid]
                name, variable = event_binding["event_parameter"], event_binding["bound_parameter"]
                _require(name not in bindings or bindings[name] == variable,
                         "Event ownership cannot replace an already fixed event binding")
                bindings[name] = variable
            parameter_types = {p["name"]: p["type"] for p in provider["parameters"]}
            for name, variable in bindings.items():
                _require(name in parameter_types, "Binding names an unavailable provider parameter")
                if isinstance(variable, dict):
                    _require(set(variable) == {"world_of"} and parameter_types[name] == "World"
                             and isinstance(variable["world_of"], str)
                             and "V" in variable_types(variable["world_of"], fixed_by_occurrence.get(oid, {}).get("scope_id")),
                             "World binding requires a visible event and an actual World-typed lexical slot")
                else:
                    _require(isinstance(variable, str) and variable in all_types,
                             "Binding names an unavailable variable")
                    _require(parameter_types[name] in variable_types(variable, fixed_by_occurrence.get(oid, {}).get("scope_id")),
                             "Ill-typed fixed lexical binding")
            hash_field = "interface_hash" if interface_only else "provider_hash"
            normalized_options.append({"synset_id": provider["synset_id"], "usage_id": provider["usage_id"],
                                       hash_field: provider["interface_hash" if interface_only else "bundle_hash"], "parameters": deepcopy(provider["parameters"]),
                                       "bindings": bindings})
        if oid in nominal_by_head:
            site = nominal_by_head[oid]
            _require(not override.get("bindings"), "Nom captures are declared in its construction; referents are enumerated")
            _require(site["usage_id"] in {o["usage_id"] for o in normalized_options},
                     "Nom's complete verb usage conflicts with selected lexical usages")
            normalized_options = list(nominal_options(site))
        lexical.append({"occurrence_id": oid, "min_calls": minimum, "max_calls": maximum, "options": normalized_options})

    slot_scopes = deepcopy(enum.get("slot_scopes", {}))
    _require(isinstance(slot_scopes, dict), "slot_scopes must be an object")
    known_slots = {}
    for resource in lexical:
        for option in resource["options"]:
            for parameter in option["parameters"]:
                key = resource["occurrence_id"] + "::" + option["usage_id"] + "::" + parameter["name"]
                known_slots[key] = parameter["type"]
    assigned_scopes = set()
    for key, sid in slot_scopes.items():
        _require(key in known_slots and isinstance(sid, str) and sid in scope_ids and sid not in assigned_scopes,
                 "slot_scopes needs a unique known lambda scope and exact provider slot")
        type_ = known_slots[key]
        _require(isinstance(type_, dict) and type_["arrow"][-1] == "Prop"
                 and type_["arrow"][:-1] == [v["type"] for v in scope_by_id[sid]["variables"]],
                 "Mapped scope variables do not match its provider function slot")
        assigned_scopes.add(sid)
    # Unmapped frozen scopes are attached exhaustively to compatible slots by
    # the engine. An explicit mapping restricts that finite assignment search.

    analyzed_nominal_heads = {a["occurrence_id"] for a in nominalization_analysis if a["decision"] == "NOMINAL_GERUND"}
    verbs = [oid for oid, row in occurrences.items() if _pos(row, "v")
             and oid not in parameter_ids and oid not in analyzed_nominal_heads]
    if "verb_occurrence_ids" in enum:
        ids = enum["verb_occurrence_ids"]
        _require(isinstance(ids, list) and len(set(ids)) == len(ids)
                 and all(isinstance(oid, str) and oid in verbs for oid in ids),
                 "verb_occurrence_ids must be distinct positively identified source verbs")
        verbs = ids
    # Legacy annotations remain readable, but no longer allocate structural
    # occurrences. The engine builds a finite typed atom set after selecting
    # lexical slots, nominal witnesses and their actual scopes.
    event_licenses, seen_event_licenses = [], set()
    for license_ in _list(enum.get("event_structure_licenses", []), "event_structure_licenses"):
        _keys(license_, {"name", "event_parameter", "max_calls", "reason"}, "event structure license")
        name, event = license_.get("name"), license_.get("event_parameter")
        _require(name in RELATIONS and isinstance(event, str) and external.get(event) == "V"
                 and type(license_.get("max_calls")) is int and license_["max_calls"] == 1
                 and _text(license_.get("reason")) and (name, event) not in seen_event_licenses,
                 "An argumentation event slot licenses one named structural call with a stated reason")
        seen_event_licenses.add((name, event))
        event_licenses.append(deepcopy(license_))
    budgets = {}
    supplied_budgets = enum.get("structural_budgets", {})
    _keys(supplied_budgets, RELATIONS, "structural_budgets")
    for name, count in supplied_budgets.items():
        _require(type(count) is int and count >= 0,
                 "Structure budget must be a nonnegative integer; typed argument pairs bound the actual atom set")
        budgets[name] = count

    def structure_rows(rows, where, *, lhs=False):
        result = []
        for row in _list(rows, where):
            _keys(row, {"name", "arguments", "scope_id"}, where + " item")
            _require(row.get("name") in RELATIONS, "Only Agent/Theme/Happen are authored structural predicates")
            args = _list(row.get("arguments"), where + ".arguments")
            _require(len(args) == 2, "Structural relations have two arguments")
            argtypes = []
            for i, arg in enumerate(args):
                if isinstance(arg, str):
                    types = variable_types(arg, row.get("scope_id"), lhs=lhs)
                    _require(bool(types), "Structural commitment uses unknown/local LHS variable")
                    argtypes.append(types)
                else:
                    _require(isinstance(arg, dict) and set(arg) == {"implicit_subject"}
                             and usage["voice"] == "passive" and row["name"] == "Agent" and i == 1
                             and arg["implicit_subject"] == args[0]
                             and "V" in variable_types(arg["implicit_subject"], row.get("scope_id"), lhs=lhs),
                             "ImplicitSubj is allowed only in passive Agent(e,ImplicitSubj(e))")
                    argtypes.append(["E"])
            signature = structures["relations"][row["name"]]["argument_types"]
            _require(all(any(actual in wanted if isinstance(wanted, list) else actual == wanted for actual in choices)
                         for choices, wanted in zip(argtypes, signature)), "Ill-typed structural commitment")
            _require(row.get("scope_id") is None or (not lhs and row["scope_id"] in scope_ids), "Invalid structural scope")
            _require(row not in result, "Duplicate structural commitment")
            result.append(deepcopy(row))
        return result

    lhs_sources = []
    if fixed is not None:
        lhs_sources.append(fixed["structural"]["lhs"])
    for container in (enum, usage):
        if "lhs_structures" in container:
            lhs_sources.append(container["lhs_structures"])
    _require(not lhs_sources or all(rows == lhs_sources[0] for rows in lhs_sources), "Conflicting LHS structure declarations")
    lhs_rows = structure_rows(lhs_sources[0] if lhs_sources else [], "lhs_structures", lhs=True)
    required = structure_rows(enum.get("required_structures", []), "required_structures")
    if fixed is not None:
        for row in structure_rows(fixed["structural"]["rhs"], "binding_plan.structural.rhs"):
            if row not in required:
                required.append(row)
    lhs = _conjunction([{"op": "target", "args": [{"var": name} for name in targets]}] + [_atom(row) for row in lhs_rows])
    lhs_names = set(targets)
    for row in lhs_rows:
        lhs_names.update(arg if isinstance(arg, str) else arg["implicit_subject"] for arg in row["arguments"])
    _require(set(external) <= lhs_names, "Fixed LHS must retain every external usage parameter")
    context = {"policy": policy, "structures": structures, "basis_ids": sorted(set(frozen_basis) |
               {p["synset_id"] for p in providers.values() if p["is_basis"]}),
               "interfaces" if interface_only else "providers": providers,
               "round": max((p.get("round", 0) for p in providers.values()), default=0) + 1,
               "mode": "interface-only-symbolic" if interface_only else "demo"}
    return {"source": source, "usage": usage, "parameters": deepcopy(usage["parameters"]),
            "target_arguments": deepcopy(targets), "lhs": lhs, "external_types": external,
            "lexical": lexical, "witnesses": list(witness_by_name.values()), "structural_budgets": budgets,
            "required_structures": required, "scope_templates": scopes, "slot_scopes": slot_scopes,
            "fixed_plan": fixed, "voice": usage["voice"], "context": context,
            "original_request": original, "head_bindings": head_bindings,
            "verb_occurrence_ids": verbs, "lhs_structures": lhs_rows,
            "parameter_projection": projection, "event_structure_licenses": event_licenses,
            "interface_assumptions": list(interface_assumptions.values()),
            "nominalizations": nominalizations, "nominalization_analysis": nominalization_analysis,
            "event_bindings": event_bindings,
            "assumption_mode": "interface-only-symbolic" if interface_only else "supplied-assumptions"}


def prepare_request(request: dict, project: str | Path | None = None) -> dict:
    """Validate and freeze an enumeration request, failing closed on malformed input."""
    try:
        return _prepare_request(request, project)
    except (TypeError, KeyError, IndexError, AttributeError) as exc:
        raise ValueError(f"Malformed enumeration input: {exc}") from exc
