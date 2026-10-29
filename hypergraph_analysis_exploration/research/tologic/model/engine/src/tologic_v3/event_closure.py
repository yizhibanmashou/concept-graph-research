"""Finite, occurrence-owned event binding; nominalized verbs are excluded.

The target's external slots never change. An ordinary verb can reuse a declared
event or license one internal V witness at its designated main-event slot.
Scope constraints are explicit, not inferred by repairing a generated RHS.
"""
from copy import deepcopy
import re

from .common import canonical_hash

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_VERBAL = {"VERBAL_NON_GERUND", "VERBAL_PROGRESSIVE_OR_PASSIVE"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _targets(node):
    if not isinstance(node, dict):
        return []
    if node.get("op") == "target":
        return [node]
    return [target for arg in node.get("args", []) for target in _targets(arg)]


def prepare_event_bindings(source, usage, enumeration, interfaces, nominalizations,
                           analyses, scopes, parameter_ids, excluded_ids, witnesses,
                           *, interface_only, policy):
    rows = enumeration.get("event_bindings", [])
    require(isinstance(rows, list), "event_bindings must be a list")
    if not rows:
        return {}, []
    require(interface_only, "Event binding currently uses explicit symbolic-interface enumeration")
    require(policy.get("schema_version") == "v3.event-closure-policy/1"
            and policy.get("version") == 1 and policy.get("max_fresh_primary_events_per_occurrence") == 1
            and policy.get("nominalized_verbs") == "Nom_only",
            "Unsupported event-closure policy")
    occurrences = {o["occurrence_id"]: o for o in source["occurrences"]}
    nominal_heads = {s["head_occurrence_id"] for s in nominalizations.values()}
    by_analysis = {a["occurrence_id"]: a for a in analyses}
    syntax_tokens = usage.get("syntax", {}).get("tokens", [])
    external = {p["name"]: p["type"] for p in usage["parameters"]}
    locals_ = {p["name"] for scope in scopes.values() for p in scope["variables"]}
    occupied = set(external) | locals_ | set(witnesses)
    disabled = {r["occurrence_id"] for r in enumeration.get("lexical", []) if r.get("max_calls") == 0}
    result, new_witnesses, introduced = {}, [], {}
    for row in rows:
        require(isinstance(row, dict) and not set(row) - {
            "occurrence_id", "usage_id", "event_parameter", "mode", "name", "parameter",
            "scope_id", "owner_occurrence_id", "within", "required", "reason"}, "Unsupported event binding fields")
        oid = row.get("occurrence_id")
        require(oid in occurrences and oid in usage["occurrence_ids"] and oid not in result
                and oid not in parameter_ids and oid not in excluded_ids and oid not in disabled,
                "Event binding needs one distinct active definition occurrence")
        require(oid not in nominal_heads and by_analysis.get(oid, {}).get("decision") != "NOMINAL_GERUND",
                "Nominalized verb occurrence is owned by Nom and cannot also license/reuse an ordinary event")
        analysis = by_analysis.get(oid)
        require(analysis is not None and analysis["decision"] in _VERBAL,
                "Ordinary event binding requires affirmative verbal syntax evidence, not an unresolved -ing form")
        token = syntax_tokens[analysis["evidence"]["token_index"]]
        require(token["pos"] in {"VERB", "AUX"} and token["dependency"] not in {"aux", "auxpass", "aux:pass", "cop"},
                "A grammatical auxiliary/copula cannot independently license an event")
        occurrence = occurrences[oid]
        require(occurrence["synset_id"].endswith("-v") or occurrence.get("pos") in {"v", "verb"},
                "Event ownership must come from a fixed verb identity")
        key = occurrence["synset_id"] + "::" + str(row.get("usage_id"))
        require(key in interfaces, "Event binding needs the exact supplied verb usage")
        interface = interfaces[key]
        parameters = interface["parameters"]
        types = {p["name"]: p["type"] for p in parameters}
        event = row.get("event_parameter")
        target_nodes = _targets(interface["lhs"])
        require(types.get(event) == "V" and len(target_nodes) == 1
                and {"var": event} in target_nodes[0]["args"],
                "Event binding must own a V slot on the verb target, not an arbitrary V complement")
        require(row.get("mode") in {"existential", "reuse"}
                and isinstance(row.get("reason"), str) and row["reason"].strip(), "Event binding needs mode and reason")
        binding = {**deepcopy(row), "synset_id": occurrence["synset_id"],
                   "event_index": next(i for i, p in enumerate(parameters) if p["name"] == event),
                   "interface_hash": interface["interface_hash"], "syntax_analysis": deepcopy(analysis),
                   "policy_hash": canonical_hash(policy)}
        if row["mode"] == "existential":
            require(not set(row) & {"parameter", "scope_id", "owner_occurrence_id"},
                    "A fresh event cannot simultaneously reuse an existing binder")
            name = row.get("name")
            require(isinstance(name, str) and _NAME.fullmatch(name) and name not in occupied,
                    "Fresh event witness cannot capture an external/local/existing witness")
            require(type(row.get("required", False)) is bool, "Event witness required must be boolean")
            occupied.add(name)
            introduced[name] = oid
            binding["bound_parameter"] = name
            witness = {"name": name, "type": "V", "origin": "verb_event", "occurrence_id": oid,
                       "head_occurrence_id": oid, "usage_id": row["usage_id"], "event_parameter": event,
                       "required": row.get("required", False), "reason": row["reason"]}
            new_witnesses.append(witness)
        else:
            require(not set(row) & {"name", "within", "required"},
                    "A reused event cannot request a new existential witness")
            require(isinstance(row.get("parameter"), str), "Reuse needs an existing parameter")
            require(not ("scope_id" in row and "owner_occurrence_id" in row), "Ambiguous reused-event owner")
            binding["bound_parameter"] = row["parameter"]
        if "within" in row:
            within = row["within"]
            require(isinstance(within, dict) and set(within) == {"occurrence_id", "usage_id", "parameter"},
                    "within must identify an exact lexical argument slot")
            owner = within["occurrence_id"]
            require(owner in occurrences and owner != oid and owner in usage["occurrence_ids"]
                    and owner not in nominal_heads and owner not in parameter_ids
                    and owner not in excluded_ids and owner not in disabled, "Invalid event-closure scope owner")
            scope_key = occurrences[owner]["synset_id"] + "::" + str(within["usage_id"])
            require(scope_key in interfaces, "Unknown event-closure scope usage")
            slot = next((p for p in interfaces[scope_key]["parameters"] if p["name"] == within["parameter"]), None)
            require(slot is not None and (slot["type"] == "Prop" or
                    isinstance(slot["type"], dict) and slot["type"].get("arrow", [None])[-1] == "Prop"),
                    "Event closure can be scoped only inside a proposition/property slot")
        result[oid] = binding
    # Resolve reused ownership only after all fresh owners are known.
    for oid, binding in result.items():
        if binding["mode"] == "reuse":
            name = binding["parameter"]
            if "scope_id" in binding:
                scope = scopes.get(binding["scope_id"])
                require(scope is not None and any(p["name"] == name and p["type"] == "V" for p in scope["variables"]),
                        "Reused scope event must be an existing V lambda parameter")
            elif "owner_occurrence_id" in binding:
                require(introduced.get(name) == binding["owner_occurrence_id"],
                        "Shared event must name its one fresh verb-occurrence owner")
            else:
                require(external.get(name) == "V", "Reused event must be an external V parameter")
        binding["binding_hash"] = canonical_hash(binding)
    return result, new_witnesses


def validate_event_bindings(prepared, rhs):
    """Check event ownership and scope for untrusted candidate ASTs too.

    No generated Nom body is traversed: authored Nom is opaque and cannot
    provide an ordinary event use or an ordinary event binder.
    """
    specifications = prepared.get("event_bindings", {})
    if not specifications:
        return []
    try:
        interfaces = prepared["context"]["interfaces"]
        calls, binders = {}, {}

        def walk(node, event_ancestors=(), lexical_slots=(), scopes=()):
            if not isinstance(node, dict):
                return
            op = node.get("op")
            if op == "nom":
                require(node.get("occurrence_id") not in specifications, "A source occurrence cannot be both Nom and an ordinary event")
                return
            if op == "exists":
                names = [p["name"] for p in node["variables"]]
                if node.get("origin") == "verb_event":
                    require(len(names) == 1 and node["variables"][0]["type"] == "V", "Each event binder binds one V witness")
                    name = names[0]
                    require(name not in binders, "Repeated event witness binder")
                    binders[name] = (node["occurrence_id"], lexical_slots)
                    event_ancestors += ((node["occurrence_id"], name),)
                walk(node["body"], event_ancestors, lexical_slots, scopes)
                return
            if op == "lambda":
                walk(node["body"], event_ancestors, lexical_slots, scopes + (node.get("scope_id"),))
                return
            if op == "use":
                oid = node["occurrence_id"]
                calls.setdefault(oid, []).append((node, event_ancestors, scopes))
                interface = interfaces[node["synset_id"] + "::" + node["usage_id"]]
                for arg, parameter in zip(node["args"], interface["parameters"]):
                    slot = (oid, node["usage_id"], parameter["name"])
                    walk(arg, event_ancestors, lexical_slots + (slot,), scopes)
                return
            for arg in node.get("args", []):
                walk(arg, event_ancestors, lexical_slots, scopes)
        walk(rhs)
        for oid, binding in specifications.items():
            own_calls = calls.get(oid, [])
            if binding["mode"] == "existential":
                name = binding["name"]
                require(bool(own_calls) == (name in binders), "An internal event and its owning verb call must occur together")
                if not own_calls:
                    continue
                require(binders[name][0] == oid, "Event binder has a different source owner")
                if "within" in binding:
                    where = binding["within"]
                    required_slot = (where["occurrence_id"], where["usage_id"], where["parameter"])
                    require(required_slot in binders[name][1], "Event existential is outside its licensed lexical scope")
            for node, ancestors, scopes in own_calls:
                require(node["usage_id"] == binding["usage_id"]
                        and node["interface_hash"] == binding["interface_hash"], "Event call changes its licensed verb usage")
                require(node["args"][binding["event_index"]] == {"var": binding["bound_parameter"]},
                        "Event witness must fill the owning verb's main-event slot")
                if binding["mode"] == "existential":
                    require((oid, binding["name"]) in ancestors, "Owning verb call must be inside its event binder")
                elif "scope_id" in binding:
                    require(binding["scope_id"] in scopes, "Reused event escapes its supplied lambda scope")
                elif "owner_occurrence_id" in binding:
                    require((binding["owner_occurrence_id"], binding["parameter"]) in ancestors,
                            "Shared event call is outside its actual owner's binder")
        declared = {b["name"] for b in specifications.values() if b["mode"] == "existential"}
        require(set(binders) <= declared, "Unlicensed event binder")
    except (ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
        return [{"code": "INVALID_EVENT_BINDING", "message": str(exc)}]
    return []
