"""Enumerate any supplied V3 input JSON using the bundled finite search engine."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ENGINE = Path(__file__).resolve().parent / "engine"
sys.path.insert(0, str(ENGINE / "src"))
from tologic_v3.common import read_json
from tologic_v3.enumeration import enumerate_request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True, help="New or empty output directory")
args = parser.parse_args()
report = enumerate_request(read_json(args.input), args.out, project=ENGINE)
print(json.dumps(report, ensure_ascii=False, indent=2))
