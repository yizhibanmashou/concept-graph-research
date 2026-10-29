# Source evidence capture contract (draft v1)

## Status and scope

The current checkout audits and reads frozen `source_record.alternative_definition_provenance.source_evidence` objects but does not contain the producer that originally wrote them. A search of `src/`, `archive/`, and `examples/` finds only consumers and audit tools. The upstream frozen bundle is configured as an external input. Therefore this contract applies **only to future captures or explicit re-acquisitions**; it does not retrofit or rewrite existing source payloads.

The machine-readable draft is [`config/source_evidence_capture.schema.json`](../config/source_evidence_capture.schema.json). It records evidence provenance, not semantic support, legal compatibility, or publication permission. The field `rights_clearance` is deliberately fixed to `not_assessed`; any later rights-holder decision must be recorded in a separate reviewed artifact.

## Binding model

One manifest record represents one `source_evidence` object and binds it using:

1. the exact frozen source payload SHA-256;
2. a zero-based ordinal in that payload's `source_evidence` array;
3. the source label and, where available, ontology ID, source record identifier, record locator, version label, and evidence type;
4. the exact producer component name/version and implementation SHA-256, plus parser and normalizer implementation SHA-256 values;
5. acquisition kind and provider version evidence.

For a static release, capture the release label, version IRI if published, serialization format, exact artifact URI, artifact SHA-256, and record-level hash if the format supports a stable record slice. For an API acquisition, capture the endpoint, request fingerprint, exact response-body SHA-256, retrieval timestamp in UTC, HTTP validators (`ETag`/`Last-Modified`) when supplied, and a source record identifier or URI. Unknown values stay `null`; a label such as `local_exact-query_cache_snapshot` must never be copied into `version_iri` or represented as an upstream release.

`identity_binding_status` and `release_binding_status` are independent. An ID resolving in a current API can establish a current identity match while the frozen release stays unbound. `verified_artifact_bytes` requires an actual artifact SHA-256. A current provider response cannot retroactively prove which historical cache bytes produced an existing payload.

## Rights references and privacy

Each provider terms reference records the evidence kind, official source URI, retrieval time, and content SHA-256. This supports future review but does not assess whether a term applies to a local record, whether licenses are compatible, or whether redistribution is authorized. Never infer a project license from the source registry's missing or present metadata alone.

The manifest may contain source identifiers and URLs and is therefore **internal-only until separately reviewed**. Do not include gloss text, source payload paths, credentials, or full source payloads. Public-facing aggregate audits should emit only counts and hashes, as in the Phase220/221 artifacts.

## Integration gate

Before connecting this contract to a source producer:

- identify and version the actual upstream acquisition code;
- record the producer implementation hash and separate parser/normalizer implementation hashes for every capture;
- have the producer emit the local payload hash and evidence ordinal at write time;
- pin the source endpoint/artifact and capture exact response or artifact bytes before parsing;
- retain the parser/normalizer implementation hash and serialization format;
- validate each manifest record against this schema with JSON Schema `format` assertions enabled;
- test that identity and release statuses cannot be promoted from a candidate join alone;
- keep a separate, human-reviewed rights/attribution decision artifact.

Until such a producer exists, current frozen records remain as observed; do not backfill a guessed release or version.

The schema requires non-empty producer and parser versions plus implementation hashes. Repository URI and revision may be null when unavailable, but the implementation hash may not: a future capture must identify the exact code bytes that wrote, parsed, or normalized the evidence. This cannot be inferred retroactively from a descriptive pipeline label in a frozen history record.

