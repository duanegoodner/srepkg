import abc
from functools import singledispatchmethod
from pathlib import Path
from typing import Callable, Union

import srepkg.construction_dir_new as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr

import srepkg.repackager_new_interfaces as re_new_int

import srepkg.shared_data_structures.new_data_structures as nds
from srepkg.utils.pkg_type_identifier import PkgRefType, PkgRefIdentifier


class ConstructionDirDispatch:

    @singledispatchmethod
    def create(self, arg) -> cdn.ConstructionDir:
        raise NotImplementedError

    @create.register
    def _(self, arg: None):
        return cdn.TempConstructionDir()

    @create.register
    def _(self, arg: str):
        return cdn.CustomConstructionDir(Path(arg))

    @create.register
    def _(self, arg: Path):
        return cdn.CustomConstructionDir(arg)


class PkgRefDispatchWithConstructionDir(abc.ABC):

    @property
    @abc.abstractmethod
    def _dispatch_table(self) -> dict[PkgRefType, Callable]:
        pass

    def create(self, pkg_ref_command: str,
               construction_dir: cdn.ConstructionDir):
        pkg_type = PkgRefIdentifier(pkg_ref_command).identify_specific_type()
        return self._dispatch_table[pkg_type](pkg_ref_command, construction_dir)


class PkgRetrieverDispatch(PkgRefDispatchWithConstructionDir):

    @property
    def _dispatch_table(self) -> dict[PkgRefType, Callable]:
        return {
            PkgRefType.LOCAL_SRC: rpr.NullPkgRetriever,
            PkgRefType.LOCAL_SDIST: rpr.NullPkgRetriever,
            PkgRefType.LOCAL_WHEEL: rpr.NullPkgRetriever,
            PkgRefType.PYPI_PKG: rpr.PyPIPkgRetriever,
            PkgRefType.GITHUB_REPO: rpr.GithubPkgRetriever
        }


class DistProviderDispatch(PkgRefDispatchWithConstructionDir):

    @property
    def _dispatch_table(self) -> dict[PkgRefType, Callable]:
        return {
            PkgRefType.LOCAL_SRC: opr.WheelAndSdistProvider,
            PkgRefType.LOCAL_SDIST: opr.DistCopyProvider,
            PkgRefType.LOCAL_WHEEL: opr.DistCopyProvider,
            PkgRefType.GITHUB_REPO: opr.WheelAndSdistProvider,
            PkgRefType.PYPI_PKG: opr.NullDistProvider
        }


class OrigSrcPreparerBuilder:

    def __init__(self,
                 construction_dir_command: Union[str, None],
                 orig_pkg_ref_command: str):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._construction_dir_dispatch = ConstructionDirDispatch()
        self._retriever_dispatch = PkgRetrieverDispatch()
        self._provider_dispatch = DistProviderDispatch()

    def create(self):
        construction_dir = self._construction_dir_dispatch.create(
            self._construction_dir_command)
        pkg_retriever = self._retriever_dispatch.create(
            self._orig_pkg_ref_command, construction_dir)
        dist_provider = self._provider_dispatch.create(
            self._orig_pkg_ref_command, construction_dir)

        return osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)


class ServiceBuilder(re_new_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: nds.SrepkgCommand):
        self._srepkg_command = srepkg_command
        self._osp_builder = OrigSrcPreparerBuilder(
            construction_dir_command=srepkg_command.construction_dir,
            orig_pkg_ref_command=srepkg_command.orig_pkg_ref)

    def create_orig_src_preparer(self) -> osp.OrigSrcPreparer:
        return self._osp_builder.create()
