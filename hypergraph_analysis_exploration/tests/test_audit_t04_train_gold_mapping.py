from types import SimpleNamespace

from src.analysis.audit_t04_train_gold_mapping import classify_gold


NODES = {"oewn-00000001-n": {"synset_id": "oewn-00000001-n"}}


def resolver_for(member_keys):
    members = [SimpleNamespace(key=lambda key=key: key) for key in member_keys]
    synset = SimpleNamespace(lemmas=lambda: members)
    return lambda _key: SimpleNamespace(synset=lambda: synset)


def test_invalid_gold_and_exact_mapping_outcomes():
    assert classify_gold(None, "1:00:00::", {}, NODES, resolver_for([])) == (
        "invalid_gold", None
    )
    assert classify_gold("lemma", "1:00:00::", {"lemma%1:00:00::": {"00000001-n"}}, NODES, resolver_for([])) == (
        "exact_unique_graph_target", None
    )
    assert classify_gold("lemma", "1:00:00::", {"lemma%1:00:00::": {"00000002-n"}}, NODES, resolver_for([])) == (
        "target_absent_from_graph", None
    )


def test_exact_key_absence_sensitivity_does_not_repair_labels():
    def invalid_resolver(_key):
        raise KeyError("not in WordNet 3.0")

    assert classify_gold("lemma", "1:00:00::", {}, NODES, invalid_resolver) == (
        "no_exact_key_invalid_in_wn30", None
    )
    assert classify_gold("lemma", "1:00:00::", {}, NODES, resolver_for(["lemma%1:00:00::"])) == (
        "no_exact_key_valid_wn30_no_oewn_member_match",
        "synset_no_oewn_member_match",
    )


def test_synset_sensitivity_distinguishes_partial_and_split_mappings():
    partial = resolver_for(["lemma%1:00:00::", "other%1:00:00::"])
    assert classify_gold(
        "lemma", "1:00:00::", {"other%1:00:00::": {"00000001-n"}}, NODES, partial
    ) == ("no_exact_key_valid_wn30_oewn_partial_single", "synset_partial_keys_one_oewn_target")

    split = resolver_for(["other%1:00:00::", "third%1:00:00::"])
    assert classify_gold(
        "lemma", "1:00:00::",
        {"other%1:00:00::": {"00000001-n"}, "third%1:00:00::": {"00000002-n"}},
        NODES,
        split,
    ) == ("no_exact_key_valid_wn30_oewn_split", "synset_member_keys_split")
