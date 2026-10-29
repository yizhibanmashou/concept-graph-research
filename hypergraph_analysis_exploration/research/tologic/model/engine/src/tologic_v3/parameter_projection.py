"""Validate explicit A/B parameter phrases without changing frozen source WSD.

A parameter phrase names an already supplied argument. Its *words* do not add
lexical conditions, while the typed variable is still passed to the formula.
Only explicit source associations remove definition occurrences from the search;
unmarked nouns and A/B support words never induce guessed source projections.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("Invalid parameter projection: " + message)


def prepare_parameter_projection(source: dict, usage: dict) -> dict:
    """Return validated finite parameter-origin exclusions and normalized spans.

Each ``usage.parameter_spans`` row has ``sentence`` (sentence_a/sentence_b),
``start``, ``end``, ``text`` and ``parameter``. ``source_occurrence_ids`` is
optional: without it, the row describes A/B support text only. With it, all
listed source occurrences must cover the exact same phrase in the definition,
and every source occurrence overlapping that slice must be listed in full.
The source, usage and their frozen WSD records are never mutated.

The caller must prevent projected IDs from being used by formula/enumeration
ASTs as well. This helper checks existing usage binding plans and witnesses;
it does not parse a candidate formula or trust prose as a binding decision.
"""
    _require(isinstance(source, dict) and isinstance(usage, dict),
             "source and usage must be objects")
    rows = usage.get("parameter_spans", [])
    _require(isinstance(rows, list), "parameter_spans must be a list")
    if not rows:
        return {"parameter_occurrence_ids": [], "covered_determiner_ids": [],
                "normalized_spans": []}
    parameters = usage.get("parameters", [])
    _require(isinstance(parameters, list), "parameters must be a list")
    external = {row.get("name") for row in parameters if isinstance(row, dict)
                and isinstance(row.get("name"), str)}
    definition = source.get("definition")
    _require(isinstance(definition, str), "definition must be text")
    occurrences = source.get("occurrences", [])
    _require(isinstance(occurrences, list), "source occurrences must be a list")
    source_by_id = {}
    for occurrence in occurrences:
        _require(isinstance(occurrence, dict)
                 and isinstance(occurrence.get("occurrence_id"), str),
                 "source occurrence needs an ID")
        oid = occurrence["occurrence_id"]
        _require(oid not in source_by_id, "duplicate source occurrence ID " + oid)
        start, end = occurrence.get("start"), occurrence.get("end")
        _require(type(start) is int and type(end) is int
                 and 0 <= start < end <= len(definition),
                 "invalid definition coordinates for " + oid)
        _require(definition[start:end] == occurrence.get("text"),
                 "definition text differs for " + oid)
        source_by_id[oid] = occurrence
    normalized = []
    intervals = {"sentence_a": [], "sentence_b": []}
    projected_parameters = {}
    for number, raw in enumerate(rows):
        label = "parameter_spans[" + str(number) + "]"
        _require(isinstance(raw, dict), label + " must be an object")
        _require(not set(raw) - {"sentence", "start", "end", "text", "parameter",
                                "source_occurrence_ids", "reason"},
                 label + " has unsupported fields")
        sentence = raw.get("sentence")
        _require(isinstance(sentence, str) and sentence in intervals,
                 label + " sentence must be sentence_a or sentence_b")
        sentence_text = usage.get(sentence)
        _require(isinstance(sentence_text, str), label + " references missing sentence")
        start, end = raw.get("start"), raw.get("end")
        _require(type(start) is int and type(end) is int
                 and 0 <= start < end <= len(sentence_text),
                 label + " coordinates must be an exact nonempty character interval")
        phrase = raw.get("text")
        _require(isinstance(phrase, str) and bool(phrase.strip())
                 and sentence_text[start:end] == phrase,
                 label + " text does not equal the sentence slice")
        # A mark may cover several words, but cannot take a prefix/suffix of one.
        _require(not (start > 0 and sentence_text[start - 1].isalnum()
                      and sentence_text[start].isalnum())
                 and not (end < len(sentence_text) and sentence_text[end - 1].isalnum()
                          and sentence_text[end].isalnum()),
                 label + " partially overlaps a word")
        parameter = raw.get("parameter")
        _require(isinstance(parameter, str) and parameter in external,
                 label + " must refer to a declared external parameter")
        _require(all(end <= previous_start or previous_end <= start
                     for previous_start, previous_end in intervals[sentence]),
                 label + " overlaps another parameter span")
        intervals[sentence].append((start, end))
        ids = raw.get("source_occurrence_ids", [])
        _require(isinstance(ids, list) and all(isinstance(oid, str) for oid in ids),
                 label + " source_occurrence_ids must be a list of IDs")
        _require(len(ids) == len(set(ids)), label + " repeats a source occurrence")
        _require(all(oid in source_by_id for oid in ids),
                 label + " references an unknown source occurrence")
        if ids:
            associated = [source_by_id[oid] for oid in ids]
            definition_start = min(item["start"] for item in associated)
            definition_end = max(item["end"] for item in associated)
            _require(definition[definition_start:definition_end] == phrase,
                     label + " source phrase does not equal marked text")
            for oid, occurrence in source_by_id.items():
                if occurrence["start"] < definition_end and definition_start < occurrence["end"]:
                    _require(definition_start <= occurrence["start"]
                             and occurrence["end"] <= definition_end and oid in ids,
                             label + " partially or incompletely covers source occurrences")
            for oid in ids:
                _require(oid not in projected_parameters or projected_parameters[oid] == parameter,
                         label + " assigns one source occurrence to different parameters")
                projected_parameters[oid] = parameter
        if "reason" in raw:
            _require(isinstance(raw["reason"], str) and bool(raw["reason"].strip()),
                     label + " reason must be nonempty text")
        record = deepcopy(raw)
        record["source_occurrence_ids"] = sorted(ids, key=lambda oid: (
            source_by_id[oid]["start"], source_by_id[oid]["end"], oid))
        normalized.append(record)
    projected = set(projected_parameters)
    fixed = usage.get("binding_plan")
    if isinstance(fixed, dict):
        for call in fixed.get("lexical", []):
            _require(not isinstance(call, dict) or call.get("occurrence_id") not in projected,
                     "parameter phrase cannot also be a lexical binding-plan call")
    for witness in usage.get("witnesses", []):
        if isinstance(witness, dict):
            _require(witness.get("occurrence_id") not in projected
                     and witness.get("article_occurrence_id") not in projected,
                     "parameter phrase cannot license an internal witness")
    for decision in usage.get("determiners", []):
        if isinstance(decision, dict) and decision.get("occurrence_id") in projected:
            _require(decision.get("action") != "exists",
                     "a parameter phrase cannot introduce an existential")
            _require(decision.get("parameter", projected_parameters[decision["occurrence_id"]])
                     == projected_parameters[decision["occurrence_id"]],
                     "determiner and parameter phrase refer to different parameters")
    covered = {oid for oid in projected
               if source_by_id[oid]["text"].casefold() in {"a", "an", "the", "all"}}
    return {"parameter_occurrence_ids": sorted(projected),
            "covered_determiner_ids": sorted(covered),
            "normalized_spans": sorted(normalized, key=lambda row: (
                row["sentence"], row["start"], row["end"]))}
