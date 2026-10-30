# MultiRD development gloss overlap audit

Question: how many official English MultiRD development definitions exactly match a graph gloss, and how many of those matching glosses also list the target word as a slash-separated graph lemma? This is a candidate-source overlap audit, not a retrieval benchmark.

Read only the `data/data_dev.json` member of the official English archive and local `OEWN/graph/nodes.tsv`. Normalize by Unicode casefold and collapsing whitespace, with no punctuation, morphology or synonym normalization. Count all rows, missing words/definitions, eligible rows, and unique target words separately. Output aggregates and SHA-256 input identities only. Empty queries do not count as nonmatches. Same lemma does not establish synset identity; exact inequality cannot rule out near duplicates or shared source families. Slash splitting can misinterpret literal slashes in a small number of labels.

The official [repository](https://github.com/thunlp/MultiRD) links its separate English data archive and labels `data_desc_c.json` as a human-description test. This audit does not read the human-description test, definition test or `data_test*` members. A repository code license does not automatically establish permission to redistribute every collected dataset; archive and outputs remain local.

From the project directory, when the data is available: `python -m src.analysis.multird_dev_overlap --archive tmp/multird_english_data.zip --nodes ../OEWN/graph/nodes.tsv --out outputs/multird_dev_overlap_20261030.json`. Fix candidate mapping, source-family overlap rules and word-level multi-sense metrics before any later independent human-description evaluation.
