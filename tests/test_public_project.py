import unittest
from pathlib import Path


class PublicProjectTest(unittest.TestCase):
    def test_hosted_app_has_only_its_runtime_dependency(self) -> None:
        requirements = Path("requirements.txt").read_text().splitlines()
        self.assertEqual(requirements, ["streamlit==1.61.1"])
        self.assertTrue(Path("requirements-benchmark.txt").exists())


if __name__ == "__main__":
    unittest.main()
