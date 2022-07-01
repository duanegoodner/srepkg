from pathlib import Path
from srepkg.srepkg import main


def test_srepkg():
    main([str(Path(__file__).parent / 'package_test_cases' / 'testproj')])
