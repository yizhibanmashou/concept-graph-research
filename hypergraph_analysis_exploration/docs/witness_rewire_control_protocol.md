# Selected-witness reuse: degree-preserving controls

Research question: under a fixed root set and bounded expansion, how does reuse of states in the selected-witness projection compare with algorithmically rewired graphs having the same directed in- and out-degrees? This is computational graph analysis, not a claim about human cognition or semantic validity.

Use the frozen witness file and existing 3,000 evaluation roots, depth 4, and a single root order with seed 17. Run capacities 0, 256 and 4096, counting computed `(node, remaining_depth)` states and percentage avoided relative to no caching within the same graph. Generate five controls independently from the original graph, seeds 101–105, each with three edge-swap attempts per original edge. Swaps preserve every node's in- and out-degree, avoid duplicate edges and newly introduced self-loops, and leave existing self-loops in place. Audit the number of accepted swaps and retained original edges. Hash input files, keep data local, and compare controls as whole graphs rather than treating their nodes as independent observations.

The randomized graphs have no semantic interpretation. This limited edge-swap walk does not guarantee uniform sampling or mixing; five controls from one graph are not independent replications of a language or population. The procedure does not preserve parts of speech, semantic roles, clause meaning, or correlations beyond degrees. Differences cannot identify a causal mechanism or establish cognitive learning.

## Post-hoc order sensitivity

After inspecting the initial outcome, repeat the same root set with order seeds 11, 23 and 31, reusing the original graph and the rewired graphs with seeds 101, 102 and 103. For each graph and order, compare capacities 256 and 4096 against that graph's uncached expansion. Graph/order cells reuse both roots and graphs and are not independent datasets. `python -m src.analysis.witness_rewire_order_sensitivity --bundle ../OEWN --roots outputs/experiment_2026_10_13/evaluation_root_ids.txt --out outputs/witness_rewire_order_sensitivity_20261030.json` reproduces the experiment from the project directory when the frozen data is present.

## Post-hoc root-source sensitivity

Partition the evaluation roots by the two largest `nodes.tsv` source labels and use order seed 17 within each group. Compare the original graph to the same two rewired graphs (seeds 101 and 102), capacities 256 and 4096, depth 4. This stratifies the roots only; rewiring does not preserve the source, POS or semantic roles of target nodes. The groups are drawn from one graph and have different sizes. They are not independent datasets, source-preserving rewires, or a basis for causal claims.

## Post-hoc source-preserving controls

Restrict edge swaps to targets with equal `source_root`, preserving directed degree and each head's counts of target source labels. Use the original 3,000 roots, order seed 17, depth 4, capacities 0/256/4096, and independent starts from the original for seeds 101/102/103, with three swap attempts per original edge. Audit actual swap counts, retained original edges and every head's source-group counts. These source labels describe the construction pipeline, not independent dictionaries; the control does not preserve exact semantic roles, POS, source clauses or meaning. Mixing and uniform sampling are not guaranteed. These graphs remain randomization diagnostics of one graph, not independent replication or cognitive evidence.
