# MultiRD development gloss overlap audit

Question: how many official English MultiRD development definitions exactly match a graph gloss, and how many of those matching glosses also list the target word as a slash-separated graph lemma? This is a candidate-source overlap audit, not a retrieval benchmark.

Read only the `data/data_dev.json` member of the official English archive and local `OEWN/graph/nodes.tsv`. Normalize by Unicode casefold and collapsing whitespace, with no punctuation, morphology or synonym normalization. Count all rows, missing words/definitions, eligible rows, and unique target words separately. Output aggregates and SHA-256 input identities only. Empty queries do not count as nonmatches. Same lemma does not establish synset identity; exact inequality cannot rule out near duplicates or shared source families. Slash splitting can misinterpret literal slashes in a small number of labels.

The official [repository](https://github.com/thunlp/MultiRD) links its separate English data archive and labels `data_desc_c.json` as a human-description test. This audit does not read the human-description test, definition test or `data_test*` members. A repository code license does not automatically establish permission to redistribute every collected dataset; archive and outputs remain local.

From the project directory, when the data is available: `python -m src.analysis.multird_dev_overlap --archive tmp/multird_english_data.zip --nodes ../OEWN/graph/nodes.tsv --out outputs/multird_dev_overlap_20261030.json`. Fix candidate mapping, source-family overlap rules and word-level multi-sense metrics before any later independent human-description evaluation.

## Development retrieval pilot (post-hoc diagnostic)

After the overlap audit, select 100 exact-gloss and 100 nonexact development rows by SHA-256 of normalized query and original row index, independently of target value and ranking. Exclude rows with empty word or definition. Run the existing untrained lexical BM25 gloss index, keep the first 100 senses, expand slash-separated lemmas in that order, deduplicate and keep the first 100 words. Score strict normalized target-word Top-1, Recall@10, truncated MRR@100 and vocabulary coverage. The 100-sense cutoff makes the word ranking incomplete; lemma order within a sense is a tie convention. Report all selected rows, with missing words and retrieval misses counted as incorrect.

The two groups are observational, not randomly assigned. They may differ in target frequency, source or query length, so performance differences cannot be causally attributed to overlap. Development records can share words or sources and are not independent human observations. This is neither an independent test nor the human-description benchmark; no test archive member is read. Run `python -m src.analysis.multird_dev_retrieval_pilot --archive tmp/multird_english_data.zip --nodes ../OEWN/graph/nodes.tsv --out outputs/multird_dev_retrieval_20261030.json` from the project directory.

## Post-hoc same-word pairs

As a further development diagnostic, select up to 100 words that have at least one exact-gloss and one nonexact development definition, ordered by the SHA-256 of the normalized word. For each word and group choose the definition with the lowest SHA-256 of normalized query plus original row index. Match the target word across conditions, but do not pass it to BM25. Use the previous cutoff and metrics, reporting vocabulary coverage and paired Top-1 discordances. This controls target word form only: a word can have different senses and the queries can differ in length, source and difficulty. The pairs are post-hoc observational diagnostics, not a causal effect or an independent test. The archive reader still accesses only `data/data_dev.json`.
