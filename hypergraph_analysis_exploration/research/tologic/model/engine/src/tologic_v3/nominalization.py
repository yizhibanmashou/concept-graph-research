"""Source-licensed gerund nominalization, kept opaque in authored formulas.

No verb identity is changed to a noun synset. A construction supplies an E
referent slot and a fixed expansion template over the complete verb interface.
NominalRef/Holds exist only in compiler-generated expansion artifacts.
"""
from copy import deepcopy
from itertools import combinations
import re

from .common import canonical_hash

RESERVED = {"NominalRef", "Holds"}
NOM_FIELDS = {"op", "synset_id", "usage_id", "interface_hash", "occurrence_id",
              "nominalization_id", "construction_hash", "negation_occurrence_ids", "args"}
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def analyze_nominalizations(source, usage):
    """Conservative classification of every mapped verb in a supplied parse.

    Surface -ing only raises a candidate. Nominal dependency evidence is also
    required. Progressive auxiliaries and ambiguous clausal complements never
    authorize Nom. This function does not parse English or redo frozen WSD.
    """
    syntax = usage.get("syntax")
    if syntax is None:
        return []
    require(isinstance(syntax, dict) and set(syntax) == {"sentence", "tokens", "provenance"},
            "Syntax needs sentence, tokens and provenance")
    side = syntax["sentence"]
    require(side in {"sentence_a", "sentence_b"} and isinstance(syntax["provenance"], str)
            and syntax["provenance"].strip(), "Syntax needs a valid A/B side and provenance")
    sentence, tokens = usage[side], syntax["tokens"]
    require(isinstance(tokens, list), "Syntax tokens must be a list")
    occurrences = {o["occurrence_id"]: o for o in source["occurrences"]}
    mapped = set()
    for i, token in enumerate(tokens):
        require(isinstance(token, dict) and token.get("index") == i
                and isinstance(token.get("start"), int) and isinstance(token.get("end"), int)
                and 0 <= token["start"] < token["end"] <= len(sentence)
                and sentence[token["start"]:token["end"]] == token.get("text")
                and isinstance(token.get("head"), int) and 0 <= token["head"] < len(tokens)
                and isinstance(token.get("dependency"), str) and isinstance(token.get("pos"), str),
                "Malformed syntax token or sentence coordinates")
        if token.get("occurrence_id") is not None:
            oid = token["occurrence_id"]
            require(oid in occurrences and oid not in mapped, "Unknown or duplicate syntax occurrence")
            occurrence = occurrences[oid]
            exact = occurrence["text"].casefold() == token["text"].casefold()
            recorded = (token.get("source_alignment") == "recorded_lemma_match"
                        and isinstance(token.get("lemma"), str)
                        and token["lemma"].casefold() == occurrence.get("stored_lemma", occurrence["text"]).casefold())
            require(exact or recorded,
                    "Syntax mapping needs exact surface or explicit recorded-lemma alignment; no guessed stems")
            mapped.add(oid)
    analyses = []
    for token in tokens:
        oid = token.get("occurrence_id")
        if oid is None:
            continue
        occurrence = occurrences[oid]
        if not (occurrence["synset_id"].endswith("-v") or occurrence.get("pos") in {"v", "verb"}):
            continue
        children = [t for t in tokens if t["index"] != token["index"] and t["head"] == token["index"]]
        auxiliary = any(t["dependency"] in {"aux", "auxpass", "aux:pass"}
                        and t.get("lemma", t["text"]).casefold() in
                        {"be", "am", "is", "are", "was", "were", "been", "being"} for t in children)
        dep = token["dependency"]
        head = tokens[token["head"]]
        gerund_form = token.get("verb_form") == "Ger" or token["text"].casefold().endswith("ing")
        nominal_position = (dep in {"pcomp", "pobj", "obj", "dobj", "csubj", "csubjpass", "csubj:pass", "nsubj", "nsubjpass"}
                            and token["head"] != token["index"])
        if dep in {"pcomp", "pobj"}:
            nominal_position = nominal_position and head["pos"] in {"ADP", "PREP"}
        if auxiliary:
            decision = "UNRESOLVED_COMPLEX_NOMINAL_CLAUSE" if nominal_position else "VERBAL_PROGRESSIVE_OR_PASSIVE"
        elif dep in {"amod", "acl", "advcl", "acl:relcl"}:
            decision = "VERBAL_OR_ADJECTIVAL_MODIFIER"
        elif gerund_form and nominal_position and token["pos"] in {"VERB", "NOUN"}:
            decision = "NOMINAL_GERUND"
        else:
            decision = "UNRESOLVED" if gerund_form else "VERBAL_NON_GERUND"
        negations = [t["occurrence_id"] for t in sorted(children, key=lambda t: t["index"])
                     if t["dependency"] == "neg" and t["text"].casefold() == "not" and t.get("occurrence_id")]
        other_content = [t["occurrence_id"] for t in children if t.get("occurrence_id")
                         and t["occurrence_id"] not in negations]
        overt_parameters, unmapped_arguments = set(), []
        for child in children:
            if child["dependency"] not in {"nsubj", "nsubjpass", "nsubj:pass", "obj", "dobj", "iobj", "obl", "poss", "nmod:poss"}:
                continue
            spans = [s for s in usage.get("parameter_spans", []) if s["sentence"] == side
                     and s["start"] <= child["start"] and s["end"] >= child["end"]]
            if spans:
                overt_parameters.update(s["parameter"] for s in spans)
            else:
                unmapped_arguments.append(child["text"])
        analyses.append({"occurrence_id": oid, "synset_id": occurrence["synset_id"],
                         "surface": token["text"], "decision": decision,
                         "dependency": dep, "governor": head["text"],
                         "negation_occurrence_ids": negations,
                         "other_definition_dependents": other_content,
                         "overt_argument_parameters": sorted(overt_parameters),
                         "unmapped_overt_arguments": unmapped_arguments,
                         "evidence": {"sentence": side, "token_index": token["index"],
                                      "start": token["start"], "end": token["end"],
                                      "syntax_provenance": syntax["provenance"]}})
    return analyses


def derive_nominalization_sites(source, usage, interfaces, capture_bindings=None):
    """Derive declarations for unambiguous nominal verbs with a known usage.

    Every mapped verb is inspected. A unique V target slot identifies the main
    event; remaining unfilled role slots are abstracted. Actual external argument
    bindings must be supplied, never guessed or silently abstracted.
    """
    declarations = []
    capture_bindings = capture_bindings or {}
    for analysis in analyze_nominalizations(source, usage):
        if analysis["decision"] != "NOMINAL_GERUND":
            continue
        choices = [p for p in interfaces.values() if p["synset_id"] == analysis["synset_id"]]
        require(len(choices) == 1, "Nom recognition needs the specific verb usage before deriving its role partition")
        interface = choices[0]
        def targets(node):
            if node.get("op") == "target":
                return [node]
            return [target for arg in node.get("args", []) if isinstance(arg, dict) for target in targets(arg)]
        kinds = {p["name"]: p["type"] for p in interface["parameters"]}
        heads = targets(interface["lhs"])
        require(len(heads) == 1, "Nom requires one complete usage target")
        events = [arg["var"] for arg in heads[0]["args"] if kinds.get(arg.get("var")) == "V"]
        require(len(events) == 1, "Ambiguous event slot needs an explicit Nom declaration")
        captures = deepcopy(capture_bindings.get(analysis["occurrence_id"], {}))
        require(set(analysis["overt_argument_parameters"]) <= set(captures.values())
                and not analysis["unmapped_overt_arguments"] and not analysis["other_definition_dependents"],
                "Nom phrase arguments/content require explicit bindings or a composed usage")
        declarations.append({"nominalization_id": "nominal_" + str(len(declarations)),
            "head_occurrence_id": analysis["occurrence_id"], "usage_id": interface["usage_id"],
            "event_parameter": events[0],
            "abstract_parameters": [name for name in kinds if name != events[0] and name not in captures],
            "captures": captures, "negation_occurrence_ids": analysis["negation_occurrence_ids"],
            "reason": "Nominal syntax established first; unique supplied verb usage and its V target determine the complete event/role template. Frozen WSD is unchanged."})
    return declarations


def prepare_nominalizations(source, usage, enumeration, interfaces, *, interface_only, policy):
    analyses = analyze_nominalizations(source, usage)
    rows = enumeration.get("nominalizations", [])
    require(isinstance(rows, list), "nominalizations must be a list")
    require(not rows or interface_only, "Nom currently uses the explicit symbolic-interface enumeration mode")
    require(not rows or usage.get("binding_plan") is None,
            "Nom enumeration uses declared construction bindings, not a legacy frozen binding_plan")
    if rows:
        require(policy.get("schema_version") == "v3.nominalization-policy/1"
                and policy.get("expansion_version") == 1 and policy.get("world_time_dimensions") is False
                and set(policy.get("reserved_internal_symbols", [])) == RESERVED
                and policy.get("internal_symbols_authorable") is False,
                "Unsupported nominalization expansion policy")
    occurrences = {o["occurrence_id"]: o for o in source["occurrences"]}
    external = {p["name"]: p["type"] for p in usage["parameters"]}
    analysis_by_id = {a["occurrence_id"]: a for a in analyses}
    result, heads = {}, set()
    for row in rows:
        require(isinstance(row, dict) and not set(row) - {
            "nominalization_id", "head_occurrence_id", "usage_id", "event_parameter",
            "abstract_parameters", "captures", "negation_occurrence_ids", "reason"},
            "Unsupported nominalization fields")
        nid, oid = row.get("nominalization_id"), row.get("head_occurrence_id")
        require(isinstance(nid, str) and _NAME.fullmatch(nid) and nid not in result
                and oid in occurrences and oid not in heads, "Nom requires unique construction and head IDs")
        require(oid in usage["occurrence_ids"] and analysis_by_id.get(oid, {}).get("decision") == "NOMINAL_GERUND",
                "Nom requires positive nominal syntax evidence; -ing alone does not license it")
        require(not analysis_by_id[oid]["other_definition_dependents"],
                "Nom phrase contains additional definition content; supply a composed usage instead of silently dropping its dependents")
        require(not analysis_by_id[oid]["unmapped_overt_arguments"],
                "Nom cannot silently abstract an overt argument without a source/parameter mapping")
        require(isinstance(row.get("reason"), str) and row["reason"].strip(), "Nom requires a construction rationale")
        key = occurrences[oid]["synset_id"] + "::" + str(row.get("usage_id"))
        require(key in interfaces, "Nom must use a supplied complete verb-usage LHS")
        interface = interfaces[key]
        params = {p["name"]: p["type"] for p in interface["parameters"]}
        event = row.get("event_parameter")
        require(params.get(event) == "V", "Nom's designated event parameter must be V")
        abstract = row.get("abstract_parameters")
        captures = row.get("captures", {})
        require(isinstance(abstract, list) and all(isinstance(n, str) for n in abstract)
                and len(set(abstract)) == len(abstract) and isinstance(captures, dict), "Malformed Nom role partition")
        require(event not in abstract and event not in captures and not set(abstract) & set(captures)
                and {event} | set(abstract) | set(captures) == set(params),
                "Every verb-usage parameter must be event-bound, role-abstracted, or explicitly captured")
        require(all(isinstance(params[n], str) for n in abstract), "Nom abstracts declared basic role types only")
        require(all(isinstance(value, str) and value in external and external[value] == params[name]
                    for name, value in captures.items()), "Nom captures must retain typed external parameters")
        require(set(analysis_by_id[oid]["overt_argument_parameters"]) <= set(captures.values()),
                "Nom must capture overt external participants rather than quantify them away")
        neg_ids = row.get("negation_occurrence_ids", [])
        require(isinstance(neg_ids, list) and neg_ids == analysis_by_id[oid]["negation_occurrence_ids"],
                "Nom negations must match attached not occurrences from syntax")
        neg_interfaces = {}
        for neg_id in neg_ids:
            choices = [p for p in interfaces.values() if p["synset_id"] == occurrences[neg_id]["synset_id"]]
            require(neg_id in usage["occurrence_ids"] and len(choices) == 1
                    and [p["type"] for p in choices[0]["parameters"]] == ["Prop"],
                    "Nom's not must have one supplied proposition-negation usage")
            neg_interfaces[neg_id] = deepcopy(choices[0])
        site = {**deepcopy(row), "captures": captures, "negation_occurrence_ids": neg_ids,
                "verb_interface": deepcopy(interface), "negation_interfaces": neg_interfaces,
                "syntax_analysis": deepcopy(analysis_by_id[oid]), "referent_type": "E",
                "nominalization_policy_hash": canonical_hash(policy)}
        site["construction_hash"] = canonical_hash(site)
        result[nid] = site
        heads.add(oid)
    parameter_only = {oid for span in usage.get("parameter_spans", []) for oid in span.get("source_occurrence_ids", [])}
    disabled = {row["occurrence_id"] for row in enumeration.get("lexical", []) if row.get("max_calls") == 0}
    nominal_content = {a["occurrence_id"] for a in analyses if a["decision"] == "NOMINAL_GERUND"
                       and a["occurrence_id"] in usage["occurrence_ids"]} - parameter_only - disabled
    require(nominal_content <= heads,
            "Recognized nominalized verb content needs an explicit/derived Nom construction; do not silently use its ordinary verb interface")
    return result, analyses


def nominal_options(site):
    interface = site["verb_interface"]
    formal = {p["name"]: p for p in interface["parameters"]}
    captures = list(site["captures"])
    referent_name = "nom_referent"
    while referent_name in formal:
        referent_name += "_"
    parameters = [{"name": referent_name, "type": "E", "role": "The nominalized abstract referent"}]
    parameters += [deepcopy(formal[n]) for n in captures]
    for count in range(len(site["negation_occurrence_ids"]) + 1):
        for negs in combinations(site["negation_occurrence_ids"], count):
            yield {"synset_id": interface["synset_id"], "usage_id": interface["usage_id"],
                   "interface_hash": interface["interface_hash"], "parameters": parameters,
                   "bindings": deepcopy(site["captures"]),
                   "nominalization_id": site["nominalization_id"], "construction_hash": site["construction_hash"],
                   "negation_occurrence_ids": list(negs),
                   "consumed_occurrence_ids": [site["head_occurrence_id"], *negs]}


def nominal_call_site(node, prepared):
    require(set(node) == NOM_FIELDS and node.get("op") == "nom", "Malformed authored Nom call")
    site = prepared.get("nominalizations", {}).get(node["nominalization_id"])
    require(site is not None and node["construction_hash"] == site["construction_hash"], "Unknown/stale Nom construction")
    interface = site["verb_interface"]
    require(node["occurrence_id"] == site["head_occurrence_id"]
            and all(node[k] == interface[k] for k in ("synset_id", "usage_id", "interface_hash")),
            "Nom changes its fixed verb identity or complete usage interface")
    option = next((o for o in nominal_options(site) if o["negation_occurrence_ids"] == node["negation_occurrence_ids"]), None)
    require(option is not None and isinstance(node["args"], list)
            and len(node["args"]) == len(option["parameters"]), "Wrong Nom negations or arity")
    return site, option


def expand_nominalizations(formula, prepared, *, expand_verb_lhs=True):
    """Compile Nom only after static validation; internal symbols never round-trip.

    The body is the complete supplied verb use. With expand_verb_lhs=True its
    complete LHS, including roles, is instantiated for inspection. No unknown
    basis RHS is invented. False preserves the use call for subsequent expansion.
    """
    from .enumeration_interfaces import instantiate_interface_call, validate_interface_candidate
    require(not validate_interface_candidate(prepared, formula), "Cannot expand an invalid authored Nom formula")
    occupied = set()

    def scan(value):
        if isinstance(value, dict):
            if "var" in value:
                occupied.add(value["var"])
            if "name" in value:
                occupied.add(value["name"])
            for child in value.values():
                scan(child)
        elif isinstance(value, list):
            for child in value:
                scan(child)
    scan(formula)

    def fresh(base):
        name = base
        while name in occupied:
            name += "_"
        occupied.add(name)
        return name

    def expand(node):
        if isinstance(node, list):
            return [expand(x) for x in node]
        if not isinstance(node, dict):
            return deepcopy(node)
        if node.get("op") != "nom":
            return {k: expand(v) for k, v in node.items()}
        site, _ = nominal_call_site(node, prepared)
        interface = site["verb_interface"]
        types = {p["name"]: p["type"] for p in interface["parameters"]}
        event_name = fresh("nom_event")
        abstract = [{"name": fresh("nom_role_" + name), "type": types[name]}
                    for name in site["abstract_parameters"]]
        mapping = {site["event_parameter"]: {"var": event_name}}
        mapping.update({name: {"var": local["name"]} for name, local in zip(site["abstract_parameters"], abstract)})
        mapping.update(dict(zip(site["captures"], deepcopy(node["args"][1:]))))
        call = {"op": "use", "synset_id": interface["synset_id"], "usage_id": interface["usage_id"],
                "interface_hash": interface["interface_hash"], "occurrence_id": node["occurrence_id"],
                "args": [mapping[p["name"]] for p in interface["parameters"]]}
        body = instantiate_interface_call(call, prepared["context"]) if expand_verb_lhs else call
        condition = {"op": "exists", "variables": [{"name": event_name, "type": "V"}], "body": body,
                     "origin": "nom_expansion", "occurrence_id": node["occurrence_id"]}
        # Negation is outside existential event closure, never exists(not(F)).
        for oid in reversed(node["negation_occurrence_ids"]):
            neg = site["negation_interfaces"][oid]
            condition = {"op": "use", "synset_id": neg["synset_id"], "usage_id": neg["usage_id"],
                         "interface_hash": neg["interface_hash"], "occurrence_id": oid, "args": [condition]}
        provenance = {"origin": "nom_expansion", "nominalization_id": node["nominalization_id"]}
        holds = {"op": "nom_internal", "name": "Holds",
                 "args": [deepcopy(node["args"][0]), *[{"var": p["name"]} for p in abstract]], **provenance}
        characterization = {"op": "iff", "left": holds, "right": condition}
        if abstract:
            characterization = {"op": "forall", "variables": abstract, "body": characterization}
        return {"op": "and", "args": [
            {"op": "nom_internal", "name": "NominalRef", "args": [deepcopy(node["args"][0])], **provenance},
            characterization]}
    return {"schema_version": "v3.nominalization-expansion/1", "publishable": False,
            "basis_expansion": "complete_lhs_only" if expand_verb_lhs else "uses_preserved",
            "formula": expand(formula)}
