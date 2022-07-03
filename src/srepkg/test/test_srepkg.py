from pathlib import Path
from srepkg.srepkg import main


def test_srepkg():
    orig_cwd_content = list(Path.cwd().iterdir())
    main([str(Path(__file__).parent / 'package_test_cases' / 'testproj')])
    for item in list(Path.cwd().iterdir()):
        if item not in orig_cwd_content:
            item.unlink()
