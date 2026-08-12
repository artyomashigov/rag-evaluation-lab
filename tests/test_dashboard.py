import json
import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import SavedResultError, load_saved_results


class DashboardDataTest(unittest.TestCase):
    def test_explorer_shows_natural_and_reranked_positions(self) -> None:
        app = AppTest.from_file(str(Path(__file__).parent.parent / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        baseline_ranks = app.dataframe[1].value
        self.assertListEqual(baseline_ranks["Final rank"].tolist(), [1, 2, 3])

        app.selectbox[1].set_value("Reranking")
        app.selectbox[2].set_value("q19")
        app.run()
        reranked = app.dataframe[1].value
        self.assertTrue((reranked["Final rank"] != reranked["Initial rank"]).any())

    def test_loads_complete_saved_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text(Path("results/answered-baseline.json").read_text())

            results = load_saved_results({"baseline": path})

        self.assertEqual(results["baseline"]["questions"][0]["question_id"], "q01")

    def test_reports_malformed_saved_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SavedResultError, "Missing saved results"):
                load_saved_results({"baseline": Path(directory) / "missing.json"})

            path = Path(directory) / "result.json"
            path.write_text("not json")

            with self.assertRaisesRegex(SavedResultError, "not valid JSON"):
                load_saved_results({"baseline": path})

            malformed = json.loads(Path("results/answered-baseline.json").read_text())
            malformed["metrics"]["retrieval_hit_rate"] = "high"
            path.write_text(json.dumps(malformed))
            with self.assertRaisesRegex(SavedResultError, "retrieval_hit_rate"):
                load_saved_results({"baseline": path})


if __name__ == "__main__":
    unittest.main()
