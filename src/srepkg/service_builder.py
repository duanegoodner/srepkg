from functools import singledispatchmethod
from pathlib import Path
from typing import Callable, NamedTuple

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


class PkgRefDispatchEntry(NamedTuple):
    retriever: Callable[..., rpr.ConstructedPkgRetriever]
    provider: Callable[..., opr.ConstructedDistProvider]


class PkgRefDispatchResult(NamedTuple):
    retriever: rpr.ConstructedPkgRetriever
    provider: opr.ConstructedDistProvider


class PkgRefDispatch:

    _dispatch_table = {
        PkgRefType.LOCAL_SRC: PkgRefDispatchEntry(
            retriever=rpr.NullPkgRetriever,
            provider=opr.WheelAndSdistProvider),
        PkgRefType.LOCAL_SDIST: PkgRefDispatchEntry(
            retriever=rpr.NullPkgRetriever,
            provider=opr.DistCopyProvider),
        PkgRefType.LOCAL_WHEEL: PkgRefDispatchEntry(
            retriever=rpr.NullPkgRetriever,
            provider=opr.DistCopyProvider),
        PkgRefType.GITHUB_REPO: PkgRefDispatchEntry(
            retriever=rpr.GithubPkgRetriever,
            provider=opr.NullDistProvider),
        PkgRefType.PYPI_PKG: PkgRefDispatchEntry(
            retriever=rpr.PyPIPkgRetriever,
            provider=opr.WheelAndSdistProvider)
    }

    def create(self, pkg_ref_command: str,
               construction_dir: opr.ConstructedDistProvider):
        pkg_type = PkgRefIdentifier(pkg_ref_command).identify_specific_type()
        dispatch_entry = self._dispatch_table[pkg_type]
        retriever = dispatch_entry.retriever(pkg_ref_command, construction_dir)
        provider = dispatch_entry.provider(pkg_ref_command, construction_dir)

        return PkgRefDispatchResult(retriever=retriever, provider=provider)


class OrigSrcPreparerBuilder:

    def __init__(self,
                 construction_dir_command: str,
                 orig_pkg_ref_command: str):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._construction_dir_dispatch = ConstructionDirDispatch()
        self._pkg_ref_dispatch = PkgRefDispatch()
        self._pkg_type_identifier = PkgRefIdentifier(orig_pkg_ref_command)

    def create(self):
        construction_dir = self._construction_dir_dispatch.create(
            self._construction_dir_command)

        pkg_ref_dispatch_results = self._pkg_ref_dispatch.create(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir)

        return osp.OrigSrcPreparer(
            retriever=pkg_ref_dispatch_results.retriever,
            provider=pkg_ref_dispatch_results.provider,
            receiver=construction_dir)


class ServiceBuilder(re_new_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: nds.SrepkgCommand):
        self._srepkg_command = srepkg_command
        self._osp_builder = OrigSrcPreparerBuilder(
            construction_dir_command=srepkg_command.construction_dir,
            orig_pkg_ref_command=srepkg_command.orig_pkg_ref)

    def create_orig_src_preparer(self) -> osp.OrigSrcPreparer:
        return self._osp_builder.create()
