import abc
from pathlib import Path
import srepkg.shared_data_structures.named_tuples as nt
import srepkg.shared_data_structures.new_data_structures as nds


class SrepkgCommandInterface(abc.ABC):

    @abc.abstractmethod
    def get_args(self) -> nds.SrepkgCommand:
        pass


class SettleableSrepkgDirInterface(abc.ABC):

    @abc.abstractmethod
    def settle(self):
        pass


class PkgDistProviderInterface(abc.ABC):

    @abc.abstractmethod
    def provide(self):
        pass


class OrigSrcPreparerInterface(abc.ABC):

    @abc.abstractmethod
    def prepare(self):
        pass

    # @property
    # @abc.abstractmethod
    # def receiver(self) -> SettleableSrepkgDirInterface:
    #     pass


class SrepkgBuilderInterface(abc.ABC):

    @abc.abstractmethod
    def build(self):
        pass


class PathCalculatorInterface(abc.ABC):

    @abc.abstractmethod
    def calc_builder_paths(self) -> tuple[nt.BuilderSrcPaths, nt.BuilderDestPaths]:
        pass


class ServiceBuilderInterface(abc.ABC):

    @abc.abstractmethod
    def create_orig_src_preparer(self) -> OrigSrcPreparerInterface:
        pass

    @abc.abstractmethod
    def create_srepkg_builder(self) -> SrepkgBuilderInterface:
        pass

    # @abc.abstractmethod
    # def create_orig_pkg_inspector(self) -> OrigPkgInspectorInterface:
    #     pass
