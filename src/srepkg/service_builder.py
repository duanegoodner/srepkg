import abc
from functools import singledispatch
from pathlib import Path
from typing import Callable, Dict, Type, Union, NamedTuple

import srepkg.construction_dir as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr
import srepkg.srepkg_builder as sbn

import srepkg.repackager_data_structs as rep_ds
import srepkg.repackager_interfaces as rep_int

from srepkg.utils.pkg_type_identifier import PkgRefType, PkgRefIdentifier


@singledispatch
def create_construction_dir(
        construction_dir_command, srepkg_name_command: str = None) \
        -> cdn.ConstructionDir:
    raise NotImplementedError


@create_construction_dir.register(type(None))
def _(construction_dir_command, srepkg_name_command: str = None):
    return cdn.TempConstructionDir(srepkg_name_command=srepkg_name_command)


@create_construction_dir.register(str)
def _(construction_dir_command, srepkg_name_command: str = None):
    return cdn.CustomConstructionDir(
        construction_dir_command=Path(construction_dir_command),
        srepkg_name_command=srepkg_name_command)


@create_construction_dir.register(Path)
def _(construction_dir_command, srepkg_name_command: str = None):
    return cdn.CustomConstructionDir(
        construction_dir_command=construction_dir_command,
        srepkg_name_command=srepkg_name_command)


class DispatchEntry(NamedTuple):
    constructor: Callable
    kwargs: dict


class PkgRefDispatchWithConstructionDir(abc.ABC):
    def __init__(self,
                 pkg_ref_command: str,
                 construction_dir: cdn.ConstructionDir,
                 ):
        self._pkg_ref_command = pkg_ref_command
        self._construction_dir = construction_dir

    @property
    @abc.abstractmethod
    def _dispatch_table(self) -> Dict[PkgRefType, DispatchEntry]:
        pass

    def create(self):
        pkg_type = PkgRefIdentifier(self._pkg_ref_command) \
            .identify_for_osp_dispatch()
        dispatch_entry = self._dispatch_table[pkg_type]
        return dispatch_entry.constructor(**dispatch_entry.kwargs)


class PkgRetrieverDispatch(PkgRefDispatchWithConstructionDir):

    @property
    def _dispatch_table(self) -> Dict[PkgRefType, DispatchEntry]:
        return {
            PkgRefType.LOCAL_SRC:
                DispatchEntry(constructor=rpr.NullPkgRetriever, kwargs={}),
            PkgRefType.LOCAL_DIST:
                DispatchEntry(constructor=rpr.NullPkgRetriever, kwargs={}),
            PkgRefType.PYPI_PKG:
                DispatchEntry(
                    constructor=rpr.PyPIPkgRetriever,
                    kwargs={
                        "pkg_ref": self._pkg_ref_command,
                        "copy_dest": self._construction_dir.orig_pkg_dists
                    }),

            PkgRefType.GITHUB_REPO:
                DispatchEntry(
                    constructor=rpr.GithubPkgRetriever,
                    kwargs={
                        "pkg_ref": self._pkg_ref_command
                    })
        }


class DistProviderDispatch(PkgRefDispatchWithConstructionDir):

    def __init__(self,
                 pkg_ref_command: str,
                 construction_dir: cdn.ConstructionDir,
                 retriever: Union[rpr.PyPIPkgRetriever, rpr.NullPkgRetriever,
                                  rpr.GithubPkgRetriever]):
        super().__init__(pkg_ref_command=pkg_ref_command,
                         construction_dir=construction_dir)
        self._retriever = retriever

    @property
    def _dispatch_table(self) -> Dict[PkgRefType, DispatchEntry]:
        return {
            PkgRefType.LOCAL_SRC:
                DispatchEntry(
                    constructor=opr.DistProviderFromSrc,
                    kwargs={
                        "src_path": Path(self._pkg_ref_command),
                        "dest_path": self._construction_dir.orig_pkg_dists
                    }),
            PkgRefType.LOCAL_DIST:
                DispatchEntry(
                    constructor=opr.DistCopyProvider,
                    kwargs={
                        "src_path": Path(self._pkg_ref_command),
                        "dest_path": self._construction_dir.orig_pkg_dists,
                    }),
            PkgRefType.GITHUB_REPO:
                DispatchEntry(
                    constructor=opr.DistProviderFromSrc,
                    kwargs={
                        "src_path": self._retriever.copy_dest,
                        "dest_path": self._construction_dir.orig_pkg_dists,
                    }),
            PkgRefType.PYPI_PKG:
                DispatchEntry(constructor=opr.NullDistProvider, kwargs={})
        }


class OrigSrcPreparerBuilder:

    def __init__(self,
                 construction_dir_command: Union[str, None],
                 orig_pkg_ref_command: str,
                 srepkg_name_command: str = None):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._srepkg_name_command = srepkg_name_command
        self._construction_dir_dispatch = create_construction_dir

    def create(self):
        construction_dir = self._construction_dir_dispatch(
            self._construction_dir_command, self._srepkg_name_command)

        pkg_retriever = PkgRetrieverDispatch(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir).create()

        dist_provider = DistProviderDispatch(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir,
            retriever=pkg_retriever
        ).create()

        return osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)


class CompleterDispatch:
    def __init__(
            self,
            construction_dir_summary: rep_ds.ConstructionDirSummary,
            completer_class: Type[sbn.SrepkgCompleter]):
        self._construction_dir_summary = construction_dir_summary
        self._completer_class = completer_class

    @property
    @abc.abstractmethod
    def _requirement_to_create(self) -> Union[Path, None]:
        pass

    def create(self):
        if self._requirement_to_create:
            return self._completer_class(
                orig_pkg_summary=self._construction_dir_summary)


class WheelCompleterDispatch(CompleterDispatch):
    def __init__(
            self,
            construction_dir_summary: rep_ds.ConstructionDirSummary):
        super().__init__(
            construction_dir_summary=construction_dir_summary,
            completer_class=sbn.SrepkgWheelCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._construction_dir_summary.src_for_srepkg_wheel


class SdistCompleterDispatch(CompleterDispatch):
    def __init__(
            self,
            construction_dir_summary: rep_ds.ConstructionDirSummary):
        super().__init__(
            construction_dir_summary=construction_dir_summary,
            completer_class=sbn.SrepkgSdistCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._construction_dir_summary.src_for_srepkg_sdist


class SrepkgBuilderBuilder:

    def __init__(
            self,
            output_dir_command: Union[str, None],
            construction_dir_summary: rep_ds.ConstructionDirSummary):
        self._construction_dir_summary = construction_dir_summary
        self._output_dir = output_dir_command

    def create(self):

        completers = [
            SdistCompleterDispatch(
                construction_dir_summary=self._construction_dir_summary
            ).create(),
            WheelCompleterDispatch(
                construction_dir_summary=self._construction_dir_summary
            ).create()
        ]

        non_null_completers = [completer for completer in completers if
                               completer is not None]

        srepkg_builder = sbn.SrepkgBuilder(
            construction_dir_summary=self._construction_dir_summary,
            srepkg_completers=non_null_completers,
            output_dir=Path(self._output_dir)
            if self._output_dir else Path.cwd()
        )

        return srepkg_builder


class ServiceBuilder(rep_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: rep_int.SrepkgCommand):
        self._srepkg_command = srepkg_command

    def create_orig_src_preparer(self) -> rep_int.OrigSrcPreparerInterface:
        osb_builder = OrigSrcPreparerBuilder(
            construction_dir_command=self._srepkg_command.construction_dir,
            orig_pkg_ref_command=self._srepkg_command.orig_pkg_ref,
            srepkg_name_command=self._srepkg_command.srepkg_name)
        return osb_builder.create()

    def create_srepkg_builder(
            self,
            construction_dir_summary: rep_ds.ConstructionDirSummary) \
            -> rep_int.SrepkgBuilderInterface:
        srepkg_builder_builder = SrepkgBuilderBuilder(
            output_dir_command=self._srepkg_command.dist_out_dir,
            construction_dir_summary=construction_dir_summary
        )
        return srepkg_builder_builder.create()
