import abc
from dataclasses import dataclass
from typing import Union

import srepkg.repackager_data_structs as rep_ds


@dataclass
class SrepkgCommand:
    orig_pkg_ref: str
    srepkg_name: Union[str, None] = None
    construction_dir: Union[str, None] = None
    dist_out_dir: Union[str, None] = None


class SrepkgCommandInterface(abc.ABC):

    @abc.abstractmethod
    def get_args(self) -> SrepkgCommand:
        pass


class PkgDistProviderInterface(abc.ABC):

    @abc.abstractmethod
    def provide(self):
        pass


class OrigSrcPreparerInterface(abc.ABC):

    @abc.abstractmethod
    def prepare(self):
        pass


class SrepkgBuilderInterface(abc.ABC):

    @abc.abstractmethod
    def build(self):
        pass


class ServiceBuilderInterface(abc.ABC):

    @abc.abstractmethod
    def create_orig_src_preparer(self) -> OrigSrcPreparerInterface:
        pass

    @abc.abstractmethod
    def create_srepkg_builder(
            self,
            construction_dir_summary: rep_ds.ConstructionDirSummary)\
            -> SrepkgBuilderInterface:
        pass
