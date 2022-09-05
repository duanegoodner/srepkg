import hashlib
import subprocess
import sys
from pathlib import Path


def md5(file_path: Path):
    hash_md5 = hashlib.md5()
    with file_path.open(mode="rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

src_path = Path("/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/"
                "testproj")
dest_path = Path("/Users/duane/srepkg_pkgs/dist_out")

pre_build_dest_contents = dest_path.iterdir()

for item in dest_path.iterdir():
    print(md5(item))


subprocess.run([
    sys.executable, "dist_builder.py", "wheel", str(src_path), str(dest_path)])

for item in dest_path.iterdir():
    print(md5(item))

print(__file__)
