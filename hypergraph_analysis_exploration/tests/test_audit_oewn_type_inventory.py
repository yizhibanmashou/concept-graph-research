import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.analysis.audit_oewn_type_inventory import audit_type_inventory


class OEWNTypeInventoryAuditTests(unittest.TestCase):
    def _release(self, root: Path):
        release_dir = root / "release"
        release_dir.mkdir()
        rows = {
            "noun.animal.json": {
                "synset-a": {"partOfSpeech": "n", "hypernym": []},
            },
            "noun.person.json": {
                "synset-b": {"partOfSpeech": "n", "hypernym": ["synset-a"]},
                "synset-c": {"partOfSpeech": "n", "instance_hypernym": ["synset-a"]},
            },
            "adj.all.json": {
                "synset-d": {"partOfSpeech": "s", "hypernym": []},
            },
        }
        archive_path = root / "oewn.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for name, content in rows.items():
                payload = json.dumps(content, sort_keys=True).encode("utf-8")
                (release_dir / name).write_bytes(payload)
                archive.writestr(name, payload)
        return release_dir, archive_path

    def test_profiles_pos_lexnames_and_keeps_hypernym_kinds_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            release_dir, archive_path = self._release(Path(directory))
            profile = audit_type_inventory(release_dir, archive_path)

        self.assertEqual(profile["synset_count"], 4)
        self.assertEqual(profile["part_of_speech_counts"], {"n": 3, "s": 1})
        self.assertEqual(profile["part_of_speech_file_mismatch_count"], 0)
        self.assertEqual(profile["relation_profiles"]["hypernym"]["edge_count"], 1)
        self.assertEqual(profile["relation_profiles"]["instance_hypernym"]["edge_count"], 1)
        self.assertEqual(
            profile["relation_profiles"]["hypernym"]["lexname_pair_counts"],
            [{"source": "noun.person", "target": "noun.animal", "edge_count": 1}],
        )
        serialized = json.dumps(profile)
        for synset_id in ("synset-a", "synset-b", "synset-c", "synset-d"):
            self.assertNotIn(synset_id, serialized)

    def test_missing_relation_endpoint_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            release_dir, archive_path = self._release(Path(directory))
            target = release_dir / "noun.person.json"
            data = json.loads(target.read_text(encoding="utf-8"))
            data["synset-b"]["hypernym"] = ["absent-synset"]
            payload = json.dumps(data, sort_keys=True).encode("utf-8")
            target.write_bytes(payload)
            with zipfile.ZipFile(archive_path, "w") as archive:
                for path in sorted(release_dir.glob("*.json")):
                    archive.write(path, path.name)

            with self.assertRaisesRegex(ValueError, "missing synset endpoint"):
                audit_type_inventory(release_dir, archive_path)


if __name__ == "__main__":
    unittest.main()
