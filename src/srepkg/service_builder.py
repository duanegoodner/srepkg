import abc
from functools import singledispatch
from pathlib import Path
from typing import Callable, Dict, Type, Union, NamedTuple

import srepkg.construction_dir as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr
import srepkg.service_registry as sr
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
    def __init__(self, pkg_ref_command: str,
                 service_registry: sr.ServiceRegistry):
        self._pkg_ref_command = pkg_ref_command
        self._service_registry = service_registry

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
                        "copy_dest": self._service_registry.get_service(
                            sr.ServiceObjectID.CONSTRUCTION_DIR).orig_pkg_dists
                    }),

            PkgRefType.GITHUB_REPO:
                DispatchEntry(
                    constructor=rpr.GithubPkgRetriever,
                    kwargs={
                        "pkg_ref": self._pkg_ref_command
                    })
        }


class DistProviderDispatch(PkgRefDispatchWithConstructionDir):

    @property
    def _dispatch_table(self) -> Dict[PkgRefType, DispatchEntry]:
        return {
            PkgRefType.LOCAL_SRC:
                DispatchEntry(
                    constructor=opr.DistProviderFromSrc,
                    kwargs={
                        "src_path": Path(self._pkg_ref_command),
                        "dest_path": self._service_registry.get_service(
                            sr.ServiceObjectID.CONSTRUCTION_DIR).orig_pkg_dists
                    }),
            PkgRefType.LOCAL_DIST:
                DispatchEntry(
                    constructor=opr.DistCopyProvider,
                    kwargs={
                        "src_path": Path(self._pkg_ref_command),
                        "dest_path": self._service_registry.get_service(
                            sr.ServiceObjectID.CONSTRUCTION_DIR).orig_pkg_dists
                    }),
            PkgRefType.GITHUB_REPO:
                DispatchEntry(
                    constructor=opr.DistProviderFromSrc,
                    kwargs={
                        "src_path": self._service_registry.get_service(
                            sr.ServiceObjectID.RETRIEVER).copy_dest,
                        "dest_path": self._service_registry.get_service(
                            sr.ServiceObjectID.CONSTRUCTION_DIR).orig_pkg_dists
                    }),
            PkgRefType.PYPI_PKG:
                DispatchEntry(constructor=opr.NullDistProvider, kwargs={})
        }


# class PkgRefDispatchWithConstructionDir(abc.ABC):
#
#     def __init__(self, pkg_ref_command: str):
#         self._pkg_ref_command = pkg_ref_command
#
#     @property
#     @abc.abstractmethod
#     def _dispatch_table(self) -> Dict[PkgRefType, Callable]:
#         pass
#
#     def create(self, construction_dir: cdn.ConstructionDir):
#         pkg_type = PkgRefIdentifier(self._pkg_ref_command).identify()
#         return self._dispatch_table[pkg_type](
#             self._pkg_ref_command, construction_dir)
#
#
# class PkgRetrieverDispatch(PkgRefDispatchWithConstructionDir):
#
#     @property
#     def _dispatch_table(self) -> Dict[PkgRefType, Callable]:
#         return {
#             PkgRefType.LOCAL_SRC: rpr.NullPkgRetriever,
#             PkgRefType.LOCAL_SDIST: rpr.NullPkgRetriever,
#             PkgRefType.LOCAL_WHEEL: rpr.NullPkgRetriever,
#             PkgRefType.PYPI_PKG: rpr.PyPIPkgRetriever,
#             PkgRefType.GITHUB_REPO: rpr.GithubPkgRetriever
#         }
#
#
# class DistProviderDispatch(PkgRefDispatchWithConstructionDir):
#
#     @property
#     def _dispatch_table(self) -> Dict[PkgRefType, Callable]:
#         return {
#             PkgRefType.LOCAL_SRC: opr.DistProviderFromSrc,
#             PkgRefType.LOCAL_SDIST: opr.DistCopyProvider,
#             PkgRefType.LOCAL_WHEEL: opr.DistCopyProvider,
#             PkgRefType.GITHUB_REPO: opr.DistProviderFromSrc,
#             PkgRefType.PYPI_PKG: opr.NullDistProvider
#         }
#

class OrigSrcPreparerBuilder:

    def __init__(self,
                 construction_dir_command: Union[str, None],
                 orig_pkg_ref_command: str,
                 service_registry: sr.ServiceRegistry,
                 srepkg_name_command: str = None):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._srepkg_name_command = srepkg_name_command
        self._service_registry = service_registry
        self._construction_dir_dispatch = create_construction_dir
        self._retriever_dispatch = PkgRetrieverDispatch(
            pkg_ref_command=orig_pkg_ref_command,
            service_registry=self._service_registry)
        self._provider_dispatch = DistProviderDispatch(
            pkg_ref_command=orig_pkg_ref_command,
            service_registry=self._service_registry)

    def create(self):
        # ConstructionDirDispatch (w/ @singledispatchmethod) can't take kwargs
        construction_dir = self._construction_dir_dispatch(
            self._construction_dir_command, self._srepkg_name_command)
        self._service_registry.register(
            {sr.ServiceObjectID.CONSTRUCTION_DIR: construction_dir})

        pkg_retriever = self._retriever_dispatch.create()
        self._service_registry.register(
            {sr.ServiceObjectID.RETRIEVER: pkg_retriever})

        dist_provider = self._provider_dispatch.create()
        self._service_registry.register(
            {sr.ServiceObjectID.PROVIDER: dist_provider})

        orig_src_preparer = osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)
        self._service_registry.register({
            sr.ServiceObjectID.ORIG_SRC_PREPARER: orig_src_preparer})

        return osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)


class CompleterDispatch:
    def __init__(
            self,
            # construction_dir: cdn.ConstructionDir,
            orig_pkg_src_summary: rep_ds.OrigPkgSrcSummary,
            completer_class: Type[sbn.SrepkgCompleter]):
        # self._construction_dir = construction_dir
        self._orig_pkg_src_summary = orig_pkg_src_summary
        self._completer_class = completer_class

    @property
    @abc.abstractmethod
    def _requirement_to_create(self) -> Union[Path, None]:
        pass

    def create(self):
        if self._requirement_to_create:
            return self._completer_class(
                # construction_dir=self._construction_dir,
                orig_pkg_summary=self._orig_pkg_src_summary)


class WheelCompleterDispatch(CompleterDispatch):
    def __init__(
            self,
            # construction_dir: cdn.ConstructionDir,
            orig_pkg_src_summary: rep_ds.OrigPkgSrcSummary):
        super().__init__(
            # construction_dir=construction_dir,
            orig_pkg_src_summary=orig_pkg_src_summary,
            completer_class=sbn.SrepkgWheelCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._orig_pkg_src_summary.src_for_srepkg_wheel


class SdistCompleterDispatch(CompleterDispatch):
    def __init__(
            self,
            construction_dir: cdn.ConstructionDir,
            orig_pkg_src_summary: rep_ds.OrigPkgSrcSummary):
        super().__init__(
            # construction_dir=construction_dir,
            orig_pkg_src_summary=orig_pkg_src_summary,
            completer_class=sbn.SrepkgSdistCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._orig_pkg_src_summary.src_for_srepkg_sdist


class SrepkgBuilderBuilder:

    def __init__(
            self,
            service_registry: sr.ServiceRegistry,
            output_dir_command: Union[str, None],
            orig_pkg_src_summary: rep_ds.OrigPkgSrcSummary):
        self._service_registry = service_registry
        self._construction_dir = service_registry.get_service(
            sr.ServiceObjectID.CONSTRUCTION_DIR)
        self._orig_pkg_src_summary = orig_pkg_src_summary
        self._output_dir = output_dir_command

    def create(self):
        completers = {
            sr.ServiceObjectID.SDIST_COMPLETER:
                SdistCompleterDispatch(
                    construction_dir=self._construction_dir,
                    orig_pkg_src_summary=self._orig_pkg_src_summary
                ).create(),
            sr.ServiceObjectID.WHEEL_COMPLETER:
                WheelCompleterDispatch(
                    # construction_dir=self._construction_dir,
                    orig_pkg_src_summary=self._orig_pkg_src_summary
                ).create()
        }

        non_null_completers = {key: value for (key, value) in
                               completers.items() if value is not None}

        srepkg_builder = sbn.SrepkgBuilder(
            # construction_dir=self._construction_dir,
            orig_pkg_src_summary=self._orig_pkg_src_summary,
            srepkg_completers=[value for (key, value) in
                               non_null_completers.items()],
            output_dir=Path(self._output_dir)
            if self._output_dir else Path.cwd()
        )

        self._service_registry.register(
            {
                **non_null_completers,
                **{sr.ServiceObjectID.BUILDER: srepkg_builder}
            })

        return srepkg_builder


class ServiceBuilder(rep_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: rep_int.SrepkgCommand):
        self._srepkg_command = srepkg_command
        self._service_registry = sr.ServiceRegistry()

    def create_orig_src_preparer(self) -> rep_int.OrigSrcPreparerInterface:
        osb_builder = OrigSrcPreparerBuilder(
            construction_dir_command=self._srepkg_command.construction_dir,
            orig_pkg_ref_command=self._srepkg_command.orig_pkg_ref,
            srepkg_name_command=self._srepkg_command.srepkg_name,
            service_registry=self._service_registry)
        return osb_builder.create()

    def create_srepkg_builder(
            self,
            orig_pkg_src_summary: rep_ds.OrigPkgSrcSummary) \
            -> rep_int.SrepkgBuilderInterface:
        srepkg_builder_builder = SrepkgBuilderBuilder(
            service_registry=self._service_registry,
            output_dir_command=self._srepkg_command.dist_out_dir,
            orig_pkg_src_summary=orig_pkg_src_summary
        )
        return srepkg_builder_builder.create()
