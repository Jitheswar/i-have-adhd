import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_manifests  # noqa: E402


class ManifestSyncTest(unittest.TestCase):
    def test_manifests_match_package_json(self):
        source = json.loads(render_manifests.SOURCE_PATH.read_text(encoding="utf8"))

        for relative_path, mapping in render_manifests.TARGETS:
            rendered = render_manifests.render_target(source, relative_path, mapping)
            current = (ROOT / relative_path).read_text(encoding="utf8")
            self.assertEqual(
                current,
                rendered,
                f"{relative_path} is out of sync with package.json; "
                "run python3 scripts/render_manifests.py",
            )


if __name__ == "__main__":
    unittest.main()
