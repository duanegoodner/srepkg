from functools import singledispatchmethod
from pathlib import Path
import repackager_interfaces as rep_int
import construction_dir as cd
import shared_data_structures as sds


class ServiceClassBuilder(rep_int.ServiceClassBuilderInterface):

    @singledispatchmethod
    def build_construction_dir(self, arg) -> rep_int.ConstructionDirInterface:
        raise NotImplementedError

    @build_construction_dir.register
    def _(self, arg: None):
        return cd.TemporaryConstructionDir()

    @build_construction_dir.register
    def _(self, arg: str):
        return cd.CustomConstructionDir(Path(arg))

    @build_construction_dir.register
    def _(self, arg: Path):
        return cd.CustomConstructionDir(arg)
