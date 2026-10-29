"""Exhaustive finite resource/region search for one V3 usage.

The adapter validates and freezes ``prepared``.  This module introduces no
lexical operators: a scope is supplied only by a selected provider argument or
an explicitly licensed existential witness.  A region contains a nonempty,
canonical conjunction.  Its members are occurrence calls, permitted structural
atoms, and licensed existential binders.  There is no depth, beam, or result cap.

Completeness is relative to that grammar (not to all of higher order logic):
every formula has a resource selection, a mode for each provider argument,
a region parent for every node, and a typed visible argument assignment.  The
loops below exhaust these finite choices; rejected partial choices violate an
explicit grammar constraint.  ``StopIteration`` alone signals exhaustion.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations, product
import json
from typing import Any, Iterator


_STRUCT_SIGNATURES = {
    "Agent": ("V", "E"),
    "Theme": ("V", ("E", "V")),
    "Happen": ("V", "Time"),
}


def _key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _inc(stats: dict, key: str, amount: int = 1) -> None:
    stats[key] = stats.get(key, 0) + amount


def _matches(actual: Any, expected: Any) -> bool:
    return actual in expected if isinstance(expected, tuple) else actual == expected


def _property_domains(type_: Any) -> list | None:
    if not isinstance(type_, dict):
        return None
    arrow = type_.get("arrow")
    if not isinstance(arrow, list) or len(arrow) < 2 or arrow[-1] != "Prop":
        raise ValueError("Enumeration supports function arguments with an explicit final Prop return type.")
    return arrow[:-1]


def _and(children: list[dict]) -> dict:
    """Flatten/sort AND without erasing repeated, provenance-bearing calls."""
    flattened = []
    for child in children:
        flattened.extend(child["args"] if child.get("op") == "and" else [child])
    flattened.sort(key=_key)
    if not flattened:
        raise ValueError("The enumeration grammar has no empty conjunction or truth constant.")
    return flattened[0] if len(flattened) == 1 else {"op": "and", "args": flattened}


def _free_vars(node: Any, bound: frozenset = frozenset()) -> set:
    if not isinstance(node, dict):
        return set()
    if set(node) == {"var"}:
        return {node["var"]} - bound
    if node.get("op") in ("lambda", "exists"):
        binders = node["parameters" if node["op"] == "lambda" else "variables"]
        return _free_vars(node["body"], bound | {p["name"] for p in binders})
    result = set()
    for value in node.values():
        if isinstance(value, dict):
            result |= _free_vars(value, bound)
        elif isinstance(value, list):
            for item in value:
                result |= _free_vars(item, bound)
    return result


def _references(node: Any) -> set:
    if isinstance(node, dict):
        if set(node) == {"var"}:
            return {node["var"]}
        return set().union(*(_references(value) for value in node.values())) if node else set()
    if isinstance(node, list):
        return set().union(*(_references(value) for value in node)) if node else set()
    return set()


def _selected_resources(prepared: dict) -> Iterator[tuple[list, list]]:
    lexical_choices = []
    cross_consumed = {oid for resource in prepared["lexical"] for option in resource["options"]
                      for oid in option.get("consumed_occurrence_ids", []) if oid != resource["occurrence_id"]}
    for resource in prepared["lexical"]:
        minimum = resource.get("min_calls", 0)
        maximum = resource.get("max_calls", 1)
        if minimum not in (0, 1) or maximum not in (0, 1) or minimum > maximum:
            raise ValueError("Each definition occurrence supplies at most one lexical call.")
        choices = ([None] if minimum == 0 or resource["occurrence_id"] in cross_consumed else [])
        if maximum:
            choices += [{**option, "occurrence_id": resource["occurrence_id"]}
                        for option in resource["options"]]
        lexical_choices.append(choices)
    for lexical in product(*lexical_choices):
        selected = [x for x in lexical if x is not None]
        consumed = [oid for call in selected for oid in call.get("consumed_occurrence_ids", [call["occurrence_id"]])]
        if len(consumed) != len(set(consumed)):
            continue
        if any(not resource["min_calls"] <= consumed.count(resource["occurrence_id"]) <= resource["max_calls"]
               for resource in prepared["lexical"]):
            continue
        witness_choices = []
        for witness in prepared.get("witnesses", []):
            if witness["origin"] == "verb_event":
                active = any(call["occurrence_id"] == witness["occurrence_id"]
                             and call["usage_id"] == witness["usage_id"]
                             and "nominalization_id" not in call for call in selected)
                witness_choices.append([witness] if active else [None])
            else:
                witness_choices.append([witness] if witness.get("required", False) else [None, witness])
        for witnesses in product(*witness_choices):
            selected_witnesses = [x for x in witnesses if x is not None]
            yield selected, selected_witnesses


def _scope_modes(nodes: list, prepared: dict, witnesses: list) -> Iterator[dict]:
    """Choose variable/generated modes and injectively realize fixed scopes."""
    templates = {s["scope_id"]: s for s in prepared.get("scope_templates", [])}
    explicit = prepared.get("slot_scopes", {})
    slots = []
    reserved_names = set(prepared["external_types"]) | {w["name"] for w in prepared.get("witnesses", [])}
    reserved_names |= {p["name"] for s in templates.values() for p in s["variables"]}
    reserved_scopes = set(templates)
    for i, node in enumerate(nodes):
        if node["kind"] != "use":
            continue
        call = node["call"]
        for j, parameter in enumerate(call["parameters"]):
            type_ = parameter["type"]
            domains = _property_domains(type_)
            if type_ != "Prop" and domains is None:
                continue
            slot_key = "::".join((call["occurrence_id"], call["usage_id"], parameter["name"]))
            slots.append((i, j, parameter, domains, slot_key))
    # Fresh names are canonical for this selected resource list and slot order.
    # Existing templates retain their given local identities.
    def fresh(base, occupied):
        value = base
        while value in occupied:
            value += "_"
        occupied.add(value)
        return value
    fresh_slots = {}
    for slot_number, (i, j, _, domains, _) in enumerate(slots):
        if domains is not None:
            sid = fresh(f"enum_scope_{slot_number}", reserved_scopes)
            variables = [{"name": fresh(f"enum_local_{slot_number}_{k}", reserved_names), "type": t}
                         for k, t in enumerate(domains)]
            fresh_slots[(i, j)] = {"scope_id": sid, "kind": "lambda", "variables": variables}

    def visit(position, modes, used):
        if position == len(slots):
            if used == set(templates):
                yield dict(modes)
            return
        i, j, parameter, domains, slot_key = slots[position]
        call = nodes[i]["call"]
        fixed_binding = call.get("bindings", {}).get(parameter["name"])
        explicit_sid = explicit.get(slot_key)
        if fixed_binding is not None and explicit_sid is not None:
            raise ValueError(f"Slot {slot_key} has both a direct binding and an explicit generated scope.")
        if explicit_sid is None:
            modes[(i, j)] = {"mode": "direct"}
            yield from visit(position + 1, modes, used)
        if fixed_binding is not None:
            return
        if domains is None:
            if explicit_sid is not None:
                raise ValueError(f"Prop slot {slot_key} cannot realize a lambda scope template.")
            modes[(i, j)] = {"mode": "generated", "kind": "prop", "variables": []}
            yield from visit(position + 1, modes, used)
            return
        choices = []
        if explicit_sid is None:
            choices.append(fresh_slots[(i, j)])
        for sid, template in templates.items():
            if sid in used or (explicit_sid is not None and sid != explicit_sid):
                continue
            if template.get("kind") != "lambda":
                raise ValueError("Native forall scope templates are outside the lexical-only enumeration grammar.")
            if [p["type"] for p in template["variables"]] == domains:
                choices.append(template)
        if explicit_sid is not None and explicit_sid not in templates:
            raise ValueError(f"Unknown explicit slot scope {explicit_sid!r}.")
        for template in choices:
            sid = template["scope_id"]
            modes[(i, j)] = {"mode": "generated", **template}
            yield from visit(position + 1, modes, used | ({sid} if sid in templates else set()))
        modes.pop((i, j), None)

    yield from visit(0, {}, set())


def _regions(nodes: list, modes: dict) -> tuple[list, dict]:
    regions = [{"owner": None, "kind": "root", "variables": []}]
    slot_regions = {}
    for (i, j), mode in modes.items():
        if mode["mode"] == "generated":
            slot_regions[(i, j)] = len(regions)
            regions.append({**mode, "owner": i, "slot": j})
    for i, node in enumerate(nodes):
        if node["kind"] == "exists":
            node["body_region"] = len(regions)
            w = node["witness"]
            regions.append({"owner": i, "kind": "exists", "variables": [{"name": w["name"], "type": w["type"]}]})
    return regions, slot_regions


def _placements(nodes: list, regions: list, may_have_prop_leaves: bool = False) -> Iterator[list]:
    """Enumerate rooted node/region trees, pruning cycles and empty regions."""
    n, r = len(nodes), len(regions)
    if not may_have_prop_leaves and (not n or r > n):
        return
    parents = [-1] * n
    counts = [0] * r
    choices = [[j for j, region in enumerate(regions) if region["owner"] != i] for i in range(n)]

    def creates_cycle(node, region_index):
        owner = regions[region_index]["owner"]
        while owner is not None:
            if owner == node:
                return True
            assigned = parents[owner]
            if assigned == -1:
                return False
            owner = regions[assigned]["owner"]
        return False

    def visit(i):
        if i == n:
            if may_have_prop_leaves or all(counts):
                yield list(parents)
            return
        for region_index in choices[i]:
            if creates_cycle(i, region_index):
                continue
            parents[i] = region_index
            counts[region_index] += 1
            if may_have_prop_leaves or sum(c == 0 for c in counts) <= n - i - 1:
                yield from visit(i + 1)
            counts[region_index] -= 1
            parents[i] = -1

    yield from visit(0)


def _environments(prepared: dict, nodes: list, regions: list, parents: list) -> tuple | None:
    environments = {0: dict(prepared["external_types"])}
    scope_chains = {0: []}
    scope_rows = []
    protected = set(prepared["external_types"]) | {w["name"] for w in prepared.get("witnesses", [])}
    pending = set(range(1, len(regions)))
    while pending:
        progressed = False
        for region_index in sorted(pending):
            region = regions[region_index]
            parent_region = parents[region["owner"]]
            if parent_region not in environments:
                continue
            environment = dict(environments[parent_region])
            chain = list(scope_chains[parent_region])
            local = {p["name"]: p["type"] for p in region["variables"]}
            if set(local) & set(environment):
                return None
            if region["kind"] == "lambda":
                if set(local) & protected:
                    return None
                nearest = chain[-1] if chain else None
                if "parent_scope" in region and region["parent_scope"] != nearest:
                    return None
                row = {"scope_id": region["scope_id"], "parent_scope": nearest,
                       "kind": "lambda", "variables": deepcopy(region["variables"])}
                scope_rows.append(row)
                chain.append(region["scope_id"])
            environment.update(local)
            environments[region_index] = environment
            scope_chains[region_index] = chain
            pending.remove(region_index)
            progressed = True
        if not progressed:
            raise AssertionError("A cyclic placement escaped structural pruning.")
    # A fixed row's scope is an ancestor constraint, as in the current V3 gate.
    fixed_rows = (prepared.get("fixed_plan") or {}).get("lexical", [])
    for i, node in enumerate(nodes):
        if node["kind"] != "use":
            continue
        call = node["call"]
        for row in fixed_rows:
            if row["occurrence_id"] == call["occurrence_id"] and row["usage_id"] == call["usage_id"]:
                sid = row.get("scope_id")
                if sid is not None and sid not in scope_chains[parents[i]]:
                    return None
    return environments, scope_chains, sorted(scope_rows, key=lambda x: x["scope_id"])


def _node_bindings(node: dict, index: int, environment: dict, modes: dict, passive: bool) -> Iterator[list]:
    if node["kind"] == "exists":
        yield []
        return
    if node["kind"] == "use":
        call = node["call"]
        choices = []
        for j, parameter in enumerate(call["parameters"]):
            mode = modes.get((index, j))
            if mode and mode["mode"] == "generated":
                choices.append([None])
                continue
            fixed = call.get("bindings", {}).get(parameter["name"])
            arguments = [{"var": name} for name, type_ in sorted(environment.items())
                         if _matches(type_, parameter["type"]) and (fixed is None or name == fixed)]
            # World is a value-producing function, not a proposition resource.
            # Its occurrence license is this source-bound provider's explicit
            # World slot. Each slot may independently reuse World(e), so the
            # finite bound comes from provider arity rather than verb counts.
            if parameter["type"] == "World":
                arguments += [{"op": "struct", "name": "World", "args": [{"var": name}]}
                              for name, type_ in sorted(environment.items())
                              if type_ == "V" and (fixed is None or fixed == {"world_of": name})]
            choices.append(arguments)
        yield from (list(args) for args in product(*choices))
        return
    name = node["name"]
    signature = _STRUCT_SIGNATURES[name]
    choices = [[{"var": var} for var, type_ in sorted(environment.items()) if _matches(type_, expected)]
               for expected in signature]
    yield from (list(args) for args in product(*choices))
    if name == "Agent" and passive:
        for event in choices[0]:
            yield [event, {"op": "struct", "name": "ImplicitSubj", "args": [deepcopy(event)]}]


def _variable_identities(prepared: dict, regions: list, parents: list) -> dict:
    """A bound variable's identity is its binder, not its surface spelling.

    Inherited variables keep their identity in nested scopes. Two sibling
    lambdas may both name a local `t` without denoting the same variable.
    """
    identities = {0: {name: ("external", name) for name in prepared["external_types"]}}
    pending = set(range(1, len(regions)))
    while pending:
        for index in sorted(pending):
            region = regions[index]
            parent = parents[region["owner"]]
            if parent in identities:
                identities[index] = {**identities[parent], **{
                    p["name"]: ("bound", index, p["name"]) for p in region["variables"]}}
                pending.remove(index)
                break
        else:
            raise AssertionError("Unresolved region in typed atom construction")
    return identities


def _structural_atom_pool(prepared: dict, regions: list, parents: list,
                          environments: dict, scope_chains: dict) -> dict:
    """Enumerate typed atoms, with alternative legal placements for each one.

    A candidate can select each (relation, bound argument identities) once.
    This is an author-level enumeration bound, not a functionality axiom.
    """
    identities = _variable_identities(prepared, regions, parents)
    pool = {name: {} for name in _STRUCT_SIGNATURES}
    fixed = prepared.get("fixed_plan")
    for region, environment in sorted(environments.items()):
        for name in _STRUCT_SIGNATURES:
            if prepared.get("structural_budgets", {}).get(name) == 0:
                continue
            for args in _node_bindings({"kind": "struct", "name": name}, 0, environment,
                                       {}, prepared.get("voice") == "passive"):
                values = [a["var"] if "var" in a else {"implicit_subject": a["args"][0]["var"]}
                          for a in args]
                if fixed is not None and not any(
                    row["name"] == name and row["arguments"] == values
                    and (row.get("scope_id") is None or row["scope_id"] in scope_chains[region])
                    for row in fixed["structural"]["rhs"]
                ):
                    continue
                bound_args = [identities[region][a["var"]] if "var" in a
                              else ("ImplicitSubj", identities[region][a["args"][0]["var"]])
                              for a in args]
                key = _key([name, bound_args])
                pool[name].setdefault(key, []).append((region, args))
    return pool


def _structural_selections(pool: dict, budgets: dict) -> Iterator[tuple[list, list, list, dict]]:
    """Choose atom subsets and one scope placement per selected atom."""
    names = list(_STRUCT_SIGNATURES)

    def visit(index, nodes, parents, bindings, counts):
        if index == len(names):
            yield nodes, parents, bindings, counts
            return
        name = names[index]
        atoms = [pool[name][key] for key in sorted(pool[name])]
        maximum = min(len(atoms), budgets.get(name, len(atoms)))
        for count in range(maximum + 1):
            for selected in combinations(atoms, count):
                for placements in product(*selected):
                    yield from visit(
                        index + 1, nodes + [{"kind": "struct", "name": name} for _ in placements],
                        parents + [region for region, _ in placements],
                        bindings + [args for _, args in placements], {**counts, name: count})

    yield from visit(0, [], [], [], {})


def _build(nodes: list, regions: list, slot_regions: dict, parents: list, bindings: list,
           scope_chains: dict, scope_rows: list, prepared: dict, prop_leaves: list) -> tuple[dict, dict]:
    children = [[] for _ in regions]
    for i, parent in enumerate(parents):
        children[parent].append(i)
    lexical_rows, structure_rows = [], []

    def region_formula(region_index):
        return _and([node_formula(i) for i in children[region_index]] +
                    [{"var": name} for name in prop_leaves[region_index]])

    def scope_field(i):
        chain = scope_chains[parents[i]]
        return {"scope_id": chain[-1]} if chain else {}

    def node_formula(i):
        node = nodes[i]
        if node["kind"] == "exists":
            w = node["witness"]
            return {"op": "exists", "variables": [{"name": w["name"], "type": w["type"]}],
                    "body": region_formula(node["body_region"]), "origin": w["origin"],
                    "occurrence_id": w["occurrence_id"]}
        args = deepcopy(bindings[i])
        if node["kind"] == "struct":
            values = [arg["var"] if "var" in arg else {"implicit_subject": arg["args"][0]["var"]} for arg in args]
            structure_rows.append({"name": node["name"], "arguments": values, **scope_field(i)})
            return {"op": "struct", "name": node["name"], "args": args}
        call = node["call"]
        direct_bindings = {}
        for j, parameter in enumerate(call["parameters"]):
            if args[j] is not None:
                argument = args[j]
                direct_bindings[parameter["name"]] = (
                    argument["var"] if "var" in argument
                    else {"world_of": argument["args"][0]["var"]})
                continue
            region_index = slot_regions[(i, j)]
            region = regions[region_index]
            body = region_formula(region_index)
            args[j] = ({"op": "lambda", "parameters": deepcopy(region["variables"]),
                        "scope_id": region["scope_id"], "body": body}
                       if region["kind"] == "lambda" else body)
        lexical_rows.append({"occurrence_id": call["occurrence_id"], "usage_id": call["usage_id"],
                             "bindings": direct_bindings, **scope_field(i)})
        if "nominalization_id" in call:
            lexical_rows[-1].update(nominalization_id=call["nominalization_id"],
                                    negation_occurrence_ids=deepcopy(call["negation_occurrence_ids"]))
            return {"op": "nom", "synset_id": call["synset_id"], "usage_id": call["usage_id"],
                    "interface_hash": call["interface_hash"], "occurrence_id": call["occurrence_id"],
                    "nominalization_id": call["nominalization_id"], "construction_hash": call["construction_hash"],
                    "negation_occurrence_ids": deepcopy(call["negation_occurrence_ids"]), "args": args}
        hash_field = "interface_hash" if "interface_hash" in call else "provider_hash"
        return {"op": "use", "synset_id": call["synset_id"], "usage_id": call["usage_id"],
                hash_field: call[hash_field], "occurrence_id": call["occurrence_id"], "args": args}

    rhs = region_formula(0)
    # Preserve input commitments even when a provider's full LHS realizes them.
    structural = deepcopy((prepared.get("fixed_plan") or {}).get("structural", {}))
    lhs = structural.get("lhs", [])
    required = deepcopy(prepared.get("required_structures", []))
    rhs_rows = structure_rows + structural.get("rhs", []) + required
    unique_rows = {_key(row): row for row in rhs_rows}
    plan = {"lexical": sorted(lexical_rows, key=_key),
            "structural": {"lhs": lhs, "rhs": [unique_rows[k] for k in sorted(unique_rows)]}}
    if scope_rows:
        plan["scopes"] = scope_rows
    return rhs, plan


def _prop_leaf_selections(environments: dict, parents: list, region_count: int,
                          predicate_count: int) -> Iterator[list]:
    """Visible proposition inputs can be conjuncts, not invented predicates.

    A repeated identical Prop leaf within one AND is represented once (AND
    idempotence).  Different scope regions retain independent choices.  The
    supplied grammar's finite connective budget still applies.
    """
    counts = [0] * region_count
    for parent in parents:
        counts[parent] += 1
    selections = []
    for region in range(region_count):
        names = sorted(name for name, type_ in environments[region].items() if type_ == "Prop")
        subsets = [[name for name, include in zip(names, bits) if include]
                   for bits in product((False, True), repeat=len(names))]
        if counts[region] == 0:
            subsets = [subset for subset in subsets if subset]
        selections.append(subsets)
    for choice in product(*selections):
        conjunctions = sum(max(count + len(leaves) - 1, 0) for count, leaves in zip(counts, choice))
        if conjunctions <= predicate_count:
            yield list(choice)


def iter_candidates(prepared: dict, stats: dict) -> Iterator[dict]:
    """Yield every distinct candidate of the validated finite input grammar.

    This does not call a semantic model or production gate.  The caller checks
    input-specific commitments (including provider-realized structural roles).
    Statistics are cumulative; they never imply that iteration is complete.
    """
    # Validate even interfaces that later happen to be unselected.
    for resource in prepared["lexical"]:
        for option in resource["options"]:
            for parameter in option["parameters"]:
                _property_domains(parameter["type"])
    for template in prepared.get("scope_templates", []):
        if template.get("kind") != "lambda":
            raise ValueError("Only lambda scope templates are supported; lexical quantifiers remain provider calls.")
    budgets = prepared.get("structural_budgets", {})
    if set(budgets) - set(_STRUCT_SIGNATURES) or any(type(n) is not int or n < 0 for n in budgets.values()):
        raise ValueError("Structural budgets require known relations and nonnegative integers")
    seen = set()
    for lexical, witnesses in _selected_resources(prepared):
        _inc(stats, "resource_selections")
        nodes = [{"kind": "use", "call": call} for call in lexical]
        nodes += [{"kind": "exists", "witness": witness} for witness in witnesses]
        for modes in _scope_modes(nodes, prepared, witnesses):
            _inc(stats, "scope_mode_selections")
            regions, slot_regions = _regions(nodes, modes)
            # Empty regions may still receive a typed structural atom or Prop
            # leaf. Check nonemptiness only after those choices are made.
            for parents in _placements(nodes, regions, may_have_prop_leaves=True):
                _inc(stats, "region_placements")
                resolved = _environments(prepared, nodes, regions, parents)
                if resolved is None:
                    _inc(stats, "rejected_scope_constraints")
                    continue
                environments, chains, scope_rows = resolved
                options = [list(_node_bindings(node, i, environments[parents[i]], modes,
                                               prepared.get("voice") == "passive"))
                           for i, node in enumerate(nodes)]
                if any(not choice for choice in options):
                    continue
                pool = _structural_atom_pool(prepared, regions, parents, environments, chains)
                for struct_nodes, struct_parents, struct_bindings, counts in _structural_selections(pool, budgets):
                    _inc(stats, "structural_atom_selections")
                    all_nodes, all_parents = nodes + struct_nodes, parents + struct_parents
                    for prop_leaves in _prop_leaf_selections(environments, all_parents, len(regions),
                                                             len(lexical) + sum(counts.values())):
                        for bindings in product(*options):
                            _inc(stats, "typed_binding_combinations")
                            rhs, plan = _build(all_nodes, regions, slot_regions, all_parents,
                                               list(bindings) + struct_bindings, chains,
                                               scope_rows, prepared, prop_leaves)
                            if _free_vars(rhs) != set(prepared["external_types"]):
                                _inc(stats, "rejected_external_coverage")
                                continue
                            references = _references(rhs)
                            if not {w["name"] for w in witnesses} <= references:
                                _inc(stats, "rejected_unused_witnesses")
                                continue
                            encoded = _key(rhs)
                            if encoded in seen:
                                _inc(stats, "duplicate_formulas")
                                continue
                            seen.add(encoded)
                            _inc(stats, "engine_candidates")
                            yield {"rhs": rhs, "binding_plan": plan,
                                   "witnesses": deepcopy(witnesses),
                                   "used_occurrence_ids": sorted(oid for call in lexical for oid in
                                                                 call.get("consumed_occurrence_ids", [call["occurrence_id"]])),
                                   "resource_counts": {"lexical_calls": len(lexical), "exists": len(witnesses),
                                                       **({"event_exists": sum(w["origin"] == "verb_event" for w in witnesses)}
                                                          if prepared.get("event_bindings") else {}),
                                                       **({"nominalizations": sum("nominalization_id" in call for call in lexical)}
                                                          if prepared.get("nominalizations") else {}),
                                                       "structures": dict(counts),
                                                       "available_structural_atoms": {name: len(atoms) for name, atoms in pool.items()},
                                                       "generated_scopes": len(regions) - 1 - len(witnesses)}}
