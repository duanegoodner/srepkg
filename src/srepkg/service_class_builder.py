import abc
from argparse import Namespace
from srepkg.construction_dir import ConstructionDir
from srepkg.orig_pkg_retriever import OrigPkgRetriever
from srepkg.orig_pkg_inspector import OrigPkgInspector
from srepkg.path_calculator import BuilderPathsCalculator
from srepkg.srepkg_builder import Builder


class ServiceClassBuilder(abc.ABC):
    def __init__(self, args: Namespace):
        self._args = args

    @abc.abstractmethod
    def build_construction_dir(self) -> ConstructionDir:
        pass

    @abc.abstractmethod
    def build_orig_pkg_retriever(self) -> OrigPkgRetriever:
        pass

    @abc.abstractmethod
    def build_orig_pkg_inspector(self) -> OrigPkgInspector:
        pass

    @abc.abstractmethod
    def build_path_calculator(self) -> BuilderPathsCalculator:
        pass

    @abc.abstractmethod
    def build_builder(self) -> Builder:
        pass




