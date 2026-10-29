"""Unpublished symbolic calls to typed LHS interfaces, without invented RHSs.

These are research artifacts, deliberately distinct from reusable V3 formula
providers. No function here expands, registers or certifies a basis definition.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .common import canonical_hash
from .nominalization import nominal_call_site
from .event_closure import validate_event_bindings


def instantiate_interface_call(call: dict, context: dict) -> dict:
    """Substitute the complete binder-free LHS of a hash-pinned interface."""
    key = str(call.get("synset_id")) + "::" + str(call.get("usage_id"))
    interface = context.get("interfaces", {}).get(key)
    if not isinstance(interface, dict) or call.get("interface_hash") != interface["interface_hash"]:
        raise ValueError("Unknown or stale symbolic interface")
    args = call.get("args")
    if not isinstance(args, list) or len(args) != len(interface["parameters"]):
        raise ValueError("Interface call arity mismatch")
    substitutions = {p["name"]: arg for p, arg in zip(interface["parameters"], args)}

    def substitute(node):
        if isinstance(node, list):
            return [substitute(x) for x in node]
        if not isinstance(node, dict):
            return deepcopy(node)
        if set(node) == {"var"}:
            return deepcopy(substitutions[node["var"]])
        result = {k: substitute(v) for k, v in node.items()}
        if node.get("op") == "target":
            result.update(synset_id=interface["synset_id"], usage_id=interface["usage_id"])
        return result

    return substitute(interface["lhs"])


def validate_interface_candidate(prepared: dict, formula: dict) -> list[dict]:
    """Static independent shape/type/resource check; never a semantic verdict.

The search contract itself has already been validated by prepare_request.
Candidate payloads are still checked rather than trusting search generation.
"""
    issues = []

    def require(test, message):
        if not test:
            raise ValueError(message)

    try:
        require(prepared.get("assumption_mode") == "interface-only-symbolic",
                "An explicit interface-only request is required")
        require(formula.get("schema_version") == "v3.interface-formula-candidate/1",
                "Not an interface formula candidate")
        require(formula.get("synset_id") == prepared["source"]["synset_id"]
                and formula.get("usage_id") == prepared["usage"]["usage_id"], "Target identity changed")
        require(formula.get("parameters") == prepared["parameters"], "External parameters changed")
        require(formula.get("lhs") == prepared["lhs"], "Usage LHS changed")
        require(formula.get("primitives") == [], "Symbolic candidates cannot declare primitives")
        external = prepared["external_types"]
        interfaces = prepared["context"]["interfaces"]
        structures = prepared["context"]["structures"]["relations"]
        resources = {r["occurrence_id"]: r for r in prepared["lexical"]}
        witnesses = {w["name"]: w for w in prepared["witnesses"]}
        used, bound_witnesses, atoms, counts = Counter(), set(), set(), Counter()
        nominal_heads = []
        free = set()

        def infer(node: Any, env: dict, bindings: dict, path: tuple, *, world_slot=False,
                  implicit_slot=None):
            require(isinstance(node, dict) and bool(node), "Missing formula AST")
            if "var" in node:
                require(set(node) == {"var"} and node["var"] in env, "Unknown or malformed variable")
                if node["var"] in external:
                    free.add(node["var"])
                return env[node["var"]]
            op = node.get("op")
            if op == "and":
                require(set(node) == {"op", "args"} and isinstance(node["args"], list)
                        and len(node["args"]) >= 2, "Malformed conjunction")
                for i, arg in enumerate(node["args"]):
                    require(infer(arg, env, bindings, path + (i,)) == "Prop", "Non-proposition conjunction")
                return "Prop"
            if op in {"lambda", "exists"}:
                field = "parameters" if op == "lambda" else "variables"
                allowed = {"op", field, "body", "scope_id"} if op == "lambda" else {
                    "op", field, "body", "origin", "occurrence_id"}
                require(not set(node) - allowed, "Unexpected binder fields")
                parameters = node.get(field)
                require(isinstance(parameters, list) and bool(parameters), "Empty binder")
                local, local_bindings = dict(env), dict(bindings)
                types = []
                for parameter in parameters:
                    require(isinstance(parameter, dict) and set(parameter) == {"name", "type"},
                            "Malformed local parameter")
                    name, kind = parameter["name"], parameter["type"]
                    require(name not in local, "Binder captures an existing external or local parameter")
                    require(kind in {"E", "V", "Time", "World", "Prop"}
                            if isinstance(kind, str) else isinstance(kind, dict) and "arrow" in kind,
                            "Unknown local type")
                    if op == "exists":
                        license_ = witnesses.get(name)
                        require(license_ is not None and license_["type"] == kind
                                and license_["origin"] == node.get("origin")
                                and license_["occurrence_id"] == node.get("occurrence_id")
                                and name not in bound_witnesses, "Unlicensed or repeated existential witness")
                        bound_witnesses.add(name)
                    local[name], local_bindings[name] = kind, (path, name)
                    types.append(kind)
                body = infer(node.get("body"), local, local_bindings, path + ("body",))
                require(body == "Prop", "Binder body must be a proposition")
                return {"arrow": types + [body]} if op == "lambda" else "Prop"
            if op == "use":
                require(set(node) == {"op", "synset_id", "usage_id", "interface_hash", "occurrence_id", "args"},
                        "Symbolic calls require interface_hash, not a formula provider hash")
                resource = resources.get(node["occurrence_id"])
                require(resource is not None, "Call is not licensed by a definition occurrence")
                options = [o for o in resource["options"] if "nominalization_id" not in o and o["synset_id"] == node["synset_id"]
                           and o["usage_id"] == node["usage_id"] and o["interface_hash"] == node["interface_hash"]]
                require(bool(options), "Call changes fixed WSD, allowed usage or interface hash")
                interface = interfaces[node["synset_id"] + "::" + node["usage_id"]]
                require(isinstance(node["args"], list) and len(node["args"]) == len(interface["parameters"]),
                        "Wrong interface arity")
                for i, (arg, parameter) in enumerate(zip(node["args"], interface["parameters"])):
                    require(infer(arg, env, bindings, path + ("arg", i),
                                  world_slot=parameter["type"] == "World") == parameter["type"],
                            "Ill-typed interface argument")
                used[node["occurrence_id"]] += 1
                return "Prop"
            if op == "nom":
                site, option = nominal_call_site(node, prepared)
                for i, (arg, parameter) in enumerate(zip(node["args"], option["parameters"])):
                    require(infer(arg, env, bindings, path + ("nom_arg", i)) == parameter["type"],
                            "Ill-typed Nom referent or capture")
                    if i:
                        require(arg == {"var": site["captures"][parameter["name"]]},
                                "Nom cannot discard, replace or abstract an external capture")
                for oid in option["consumed_occurrence_ids"]:
                    used[oid] += 1
                nominal_heads.append((site["head_occurrence_id"], node["args"][0]))
                return "Prop"
            if op == "struct":
                require(set(node) == {"op", "name", "args"}, "Malformed structural call")
                name, args = node["name"], node["args"]
                require(name in structures and isinstance(args, list), "Unknown structural symbol")
                signature = structures[name]
                require(len(args) == len(signature["argument_types"]), "Wrong structural arity")
                if name == "World":
                    require(world_slot and len(args) == 1 and set(args[0]) == {"var"},
                            "World(e) is allowed only in a known World lexical slot")
                elif name == "ImplicitSubj":
                    require(prepared["voice"] == "passive" and implicit_slot is not None
                            and args == [implicit_slot], "ImplicitSubj only in passive Agent(e,ImplicitSubj(e))")
                for i, (arg, wanted) in enumerate(zip(args, signature["argument_types"])):
                    actual = infer(arg, env, bindings, path + ("arg", i),
                                   implicit_slot=args[0] if name == "Agent" and i == 1 else None)
                    require(actual in wanted if isinstance(wanted, list) else actual == wanted,
                            "Ill-typed structural argument")
                if signature["return_type"] == "Prop":
                    require(name in {"Agent", "Theme", "Happen"}, "Unauthorized authored predicate")
                    def term_identity(arg):
                        if "var" in arg:
                            return bindings[arg["var"]]
                        return (arg["name"], tuple(term_identity(a) for a in arg["args"]))
                    identity = canonical_hash([name, [term_identity(a) for a in args]])
                    require(identity not in atoms, "Repeated structural atom for identical bound parameters")
                    atoms.add(identity)
                    counts[name] += 1
                return signature["return_type"]
            raise ValueError("Unauthorized symbolic AST operation: " + str(op))

        require(infer(formula.get("rhs"), dict(external), {n: ("external", n) for n in external}, ()) == "Prop",
                "RHS must be a proposition")
        require(set(external) <= free, "RHS drops an external parameter")
        for oid, resource in resources.items():
            require(resource["min_calls"] <= used[oid] <= resource["max_calls"], "Occurrence count outside its budget")
        for name, limit in prepared["structural_budgets"].items():
            require(counts[name] <= limit, "Structural atom count outside its budget")
        require({w["name"] for w in witnesses.values() if w["required"]} <= bound_witnesses,
                "Required internal witness absent")
        for name in bound_witnesses:
            witness = witnesses[name]
            if witness["origin"] == "nominalization":
                require((witness["head_occurrence_id"], {"var": name}) in nominal_heads,
                        "A Nom witness must be the referent of its own nominalized source head")
        issues.extend(validate_event_bindings(prepared, formula["rhs"]))
    except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        issues.append({"code": "INVALID_SYMBOLIC_CANDIDATE", "message": str(exc)})
    return issues
