import tempfile
from pathlib import Path
import repackager_interfaces as rep_int


class CustomConstructionDir(rep_int.ConstructionDirInterface):
    def __init__(self, construction_dir: Path):
        super().__init__(construction_dir)

    def settle(self):
        print(f"An uncompressed copy of {self._srepkg.name} has been saved in "
              f"{str(self._srepkg_root)}")


class TemporaryConstructionDir(rep_int.ConstructionDirInterface):
    def __init__(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(Path(self._temp_dir_obj.name))

    def settle(self):
        self._temp_dir_obj.cleanup()
