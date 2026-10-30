"""Validate and transform text-free T02 branch records.

This module accepts already curated records. It does not infer relation labels,
read OEWN files, or emit gloss text. Unknown relations remain explicit.
"""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any


SCHEMA_VERSION = "t02-relation-v0"
CONDITIONS = ("source", "prep_delete", "boundary_preserve", "typed_relation")
RELATION_CATEGORIES = {
    "spatial_location",
    "direction_path",
    "participant_role",
    "negation_absence",
    "unresolved",
}
POLARITIES = {"positive", "negative", "unknown"}
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_source_record(record: dict[str, Any]) -> None:
    """Raise ``ValueError`` unless *record* satisfies the text-free schema v0."""
    _require(isinstance(record, dict), "record must be an object")
    _require(record.get("schema_version") == SCHEMA_VERSION, "unsupported schema_version")
    for key in ("item_id", "target_id", "transform_version"):
        _require(isinstance(record.get(key), str) and bool(record[key].strip()), f"{key} must be non-empty")

    version = record.get("source_version")
    _require(isinstance(version, dict), "source_version must be an object")
    for key in ("nodes_sha256", "rules_sha256", "input_sha256"):
        _require(isinstance(version.get(key), str) and HEX_SHA256.fullmatch(version[key]) is not None,
                 f"source_version.{key} must be lowercase SHA-256")

    branches = record.get("source_branches")
    occurrences = record.get("occurrences")
    _require(isinstance(branches, list) and bool(branches), "source_branches must be a non-empty list")
    _require(isinstance(occurrences, list), "occurrences must be a list")
    branch_ids: set[str] = set()
    occurrence_ids: set[str] = set()
    occurrence_by_id: dict[str, dict[str, Any]] = {}
    for occurrence in occurrences:
        _require(isinstance(occurrence, dict), "each occurrence must be an object")
        oid = occurrence.get("occurrence_id")
        _require(isinstance(oid, str) and bool(oid.strip()) and oid not in occurrence_ids,
                 "occurrence_id must be non-empty and unique")
        occurrence_ids.add(oid)
        occurrence_by_id[oid] = occurrence
        _require(isinstance(occurrence.get("branch_id"), str), f"occurrence {oid}: branch_id required")
        _require(type(occurrence.get("branch_position")) is int and occurrence["branch_position"] >= 0,
                 f"occurrence {oid}: branch_position must be a non-negative integer")
        _require(isinstance(occurrence.get("node_id"), str) and bool(occurrence["node_id"].strip()),
                 f"occurrence {oid}: node_id required")
        _require(isinstance(occurrence.get("pos"), str) and bool(occurrence["pos"].strip()),
                 f"occurrence {oid}: pos required")
        _require(isinstance(occurrence.get("source_locator"), dict) and bool(occurrence["source_locator"]),
                 f"occurrence {oid}: source_locator required")

    for branch in branches:
        _require(isinstance(branch, dict), "each source branch must be an object")
        bid = branch.get("branch_id")
        _require(isinstance(bid, str) and bool(bid.strip()) and bid not in branch_ids,
                 "branch_id must be non-empty and unique")
        branch_ids.add(bid)
        refs = branch.get("premise_occurrence_ids")
        _require(isinstance(refs, list), f"branch {bid}: premise_occurrence_ids must be a list")
        _require(bool(refs), f"branch {bid}: source premises cannot be empty")
        _require(all(isinstance(ref, str) and bool(ref.strip()) for ref in refs),
                 f"branch {bid}: occurrence references must be non-empty strings")
        _require(len(refs) == len(set(refs)),
                 f"branch {bid}: premise_occurrence_ids must be a duplicate-free list")
        resolved = []
        for ref in refs:
            _require(ref in occurrence_by_id, f"branch {bid}: unknown occurrence reference {ref}")
            occurrence = occurrence_by_id[ref]
            _require(occurrence["branch_id"] == bid, f"branch {bid}: occurrence {ref} belongs to another branch")
            resolved.append(occurrence)
        _require([row["branch_position"] for row in resolved] == list(range(len(resolved))),
                 f"branch {bid}: occurrence order must be contiguous and match premise order")

    _require({row["branch_id"] for row in occurrences} == branch_ids,
             "every occurrence must belong to exactly one listed source branch")


def _validate_relations(record: dict[str, Any], relations: list[dict[str, Any]]) -> None:
    branch_by_id = {row["branch_id"]: row for row in record["source_branches"]}
    occurrence_by_id = {row["occurrence_id"]: row for row in record["occurrences"]}
    seen_sources: set[str] = set()
    relation_ids: set[str] = set()
    for relation in relations:
        _require(isinstance(relation, dict), "each relation must be an object")
        rid = relation.get("relation_id")
        _require(isinstance(rid, str) and bool(rid.strip()) and rid not in relation_ids,
                 "relation_id must be non-empty and unique")
        relation_ids.add(rid)
        bid = relation.get("branch_id")
        _require(bid in branch_by_id, f"relation {rid}: unknown branch_id")
        source_ids = relation.get("source_occurrence_ids")
        _require(isinstance(source_ids, list) and bool(source_ids) and len(source_ids) == len(set(source_ids)),
                 f"relation {rid}: source_occurrence_ids must be a non-empty unique list")
        for oid in source_ids:
            _require(oid in occurrence_by_id, f"relation {rid}: unknown source occurrence {oid}")
            occurrence = occurrence_by_id[oid]
            _require(occurrence["branch_id"] == bid and occurrence["pos"] == "prep",
                     f"relation {rid}: source occurrence must be a prep in the same branch")
            _require(oid not in seen_sources, f"prep occurrence {oid} cannot be rewritten twice")
            seen_sources.add(oid)
        category = relation.get("category")
        _require(category in RELATION_CATEGORIES, f"relation {rid}: unsupported category")
        status = relation.get("status")
        _require(status in {"supported", "unresolved"}, f"relation {rid}: unsupported status")
        _require(relation.get("polarity") in POLARITIES, f"relation {rid}: invalid polarity")
        _require("negation_scope" in relation, f"relation {rid}: negation_scope field required")
        if status == "supported":
            _require(category != "unresolved", f"relation {rid}: supported relation cannot be unresolved category")
            _require(isinstance(relation.get("predicate"), str) and bool(relation["predicate"].strip()),
                     f"relation {rid}: supported relation needs a predicate")
            arguments = relation.get("arguments")
            _require(isinstance(arguments, list) and len(arguments) >= 2,
                     f"relation {rid}: supported relation needs ordered arguments")
            _require(isinstance(relation.get("evidence_refs"), list) and bool(relation["evidence_refs"]),
                     f"relation {rid}: supported relation needs evidence_refs")
            scope = relation["negation_scope"]
            _require(scope == "unknown" or isinstance(scope, (str, dict)),
                     f"relation {rid}: negation_scope must be a locator or unknown")
            for argument in arguments:
                _require(isinstance(argument, dict) and isinstance(argument.get("role"), str)
                         and bool(argument["role"].strip()), f"relation {rid}: each argument needs an ordered role")
                ref = argument.get("occurrence_ref")
                _require(ref in occurrence_by_id and occurrence_by_id[ref]["branch_id"] == bid,
                         f"relation {rid}: argument occurrence must belong to the same branch")
        else:
            _require(category == "unresolved", f"relation {rid}: unresolved status requires unresolved category")
            _require(not relation.get("predicate"), f"relation {rid}: unresolved relation cannot assert a predicate")
            _require(isinstance(relation.get("unresolved_reason"), str)
                     and bool(relation["unresolved_reason"].strip()),
                     f"relation {rid}: unresolved_reason required")


def transform_record(record: dict[str, Any], relations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return four condition views without mutating input or inferring semantics.

    ``relations`` must contain independently curated relation records. Unmapped
    prepositions remain in the typed-relation premises and are listed unresolved.
    """
    validate_source_record(record)
    relations = deepcopy(relations or [])
    _validate_relations(record, relations)
    occurrence_by_id = {row["occurrence_id"]: row for row in record["occurrences"]}
    relations_by_branch: dict[str, list[dict[str, Any]]] = {row["branch_id"]: [] for row in record["source_branches"]}
    for relation in relations:
        relations_by_branch[relation["branch_id"]].append(relation)

    outputs: dict[str, Any] = {"item_id": record["item_id"], "conditions": {}}
    for condition in CONDITIONS:
        branch_rows = []
        for branch in record["source_branches"]:
            refs = list(branch["premise_occurrence_ids"])
            preps = [oid for oid in refs if occurrence_by_id[oid]["pos"] == "prep"]
            if condition == "prep_delete":
                kept = [oid for oid in refs if oid not in preps]
                boundary = []
            else:
                kept = list(refs)
                boundary = []
                if condition in {"boundary_preserve", "typed_relation"}:
                    for oid in preps:
                        index = refs.index(oid)
                        boundary.append({
                            "occurrence_id": oid,
                            "left_occurrence_id": refs[index - 1] if index else None,
                            "right_occurrence_id": refs[index + 1] if index + 1 < len(refs) else None,
                            "status": "unresolved",
                        })
            branch_relations = deepcopy(relations_by_branch[branch["branch_id"]]) if condition == "typed_relation" else []
            replaced = {
                oid for relation in branch_relations if relation["status"] == "supported"
                for oid in relation["source_occurrence_ids"]
            }
            if condition == "typed_relation":
                kept = [oid for oid in kept if oid not in replaced]
                unresolved_ids = {
                    oid for relation in branch_relations if relation["status"] == "unresolved"
                    for oid in relation["source_occurrence_ids"]
                }
                branch_relations.extend({
                    "relation_id": f"unresolved:{oid}", "branch_id": branch["branch_id"],
                    "source_occurrence_ids": [oid], "category": "unresolved", "predicate": None,
                    "arguments": [], "polarity": "unknown", "negation_scope": "unknown", "status": "unresolved",
                    "unresolved_reason": "no_curated_relation_record",
                } for oid in preps if oid not in replaced and oid not in unresolved_ids)
                boundary = [row for row in boundary if row["occurrence_id"] not in replaced]
            branch_rows.append({
                "branch_id": branch["branch_id"],
                "premise_occurrence_ids": kept,
                "removed_occurrence_ids": preps if condition == "prep_delete" else [],
                "boundaries": boundary,
                "relations": branch_relations,
                "empty_after_transform": not kept and not branch_relations,
            })
        outputs["conditions"][condition] = {"branches": branch_rows}
    return outputs
