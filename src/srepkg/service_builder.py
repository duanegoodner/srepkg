import abc
from functools import singledispatchmethod
from pathlib import Path
from typing import Callable, Type, Union

import srepkg.construction_dir_new as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr
import srepkg.service_registry as sr
import srepkg.srepkg_builder_new as sbn

import srepkg.repackager_interfaces as re_new_int
import srepkg.srepkg_builder_new_ds_and_int as sb_new_int

import srepkg.shared_data_structures.new_data_structures as nds
from srepkg.utils.pkg_type_identifier import PkgRefType, PkgRefIdentifier


class ConstructionDirDispatch:

    @singledispatchmethod
    def create(self, construction_dir_command,
               srepkg_name_command: str = None) -> cdn.ConstructionDir:
        raise NotImplementedError

    @create.register(type(None))
    def _(self, construction_dir_command, srepkg_name_command: str = None):
        return cdn.TempConstructionDir(srepkg_name_command=srepkg_name_command)

    @create.register(str)
    def _(self, construction_dir_command, srepkg_name_command: str = None):
        return cdn.CustomConstructionDir(
            construction_dir_command=Path(construction_dir_command),
            srepkg_name_command=srepkg_name_command)

    @create.register(Path)
    def _(self, construction_dir_command, srepkg_name_command: str = None):
        return cdn.CustomConstructionDir(
            construction_dir_command=construction_dir_command,
            srepkg_name_command=srepkg_name_command)


class PkgRefDispatchWithConstructionDir(abc.ABC):

    def __init__(self, pkg_ref_command: str):
        self._pkg_ref_command = pkg_ref_command

    @property
    @abc.abstractmethod
    def _dispatch_table(self) -> dict[PkgRefType, Callable]:
        pass

    def create(self, construction_dir: cdn.ConstructionDir):
        pkg_type = PkgRefIdentifier(self._pkg_ref_command).identify()
        return self._dispatch_table[pkg_type](
            self._pkg_ref_command, construction_dir)


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
            PkgRefType.LOCAL_SRC: opr.DistProviderFromSrc,
            PkgRefType.LOCAL_SDIST: opr.DistCopyProvider,
            PkgRefType.LOCAL_WHEEL: opr.DistCopyProvider,
            PkgRefType.GITHUB_REPO: opr.DistProviderFromSrc,
            PkgRefType.PYPI_PKG: opr.NullDistProvider
        }


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
        self._construction_dir_dispatch = ConstructionDirDispatch()
        self._retriever_dispatch = PkgRetrieverDispatch(
            pkg_ref_command=orig_pkg_ref_command)
        self._provider_dispatch = DistProviderDispatch(
            pkg_ref_command=orig_pkg_ref_command)

    def create(self):
        # ConstructionDirDispatch (w/ @singledispatchmethod) can't take kwargs
        construction_dir = self._construction_dir_dispatch.create(
            self._construction_dir_command, self._srepkg_name_command)
        pkg_retriever = self._retriever_dispatch.create(
            construction_dir=construction_dir)
        dist_provider = self._provider_dispatch.create(
            construction_dir=construction_dir)

        orig_src_preparer = osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)

        self._service_registry.register({
            sr.ServiceObjectID.ORIG_SRC_PREPARER: orig_src_preparer,
            sr.ServiceObjectID.CONSTRUCTION_DIR: construction_dir,
            sr.ServiceObjectID.RETRIEVER: pkg_retriever,
            sr.ServiceObjectID.PROVIDER: dist_provider
        })

        return osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)


class CompleterDispatch:
    def __init__(
            self,
            construction_dir: cdn.ConstructionDir,
            completer_class: Type[sbn.SrepkgCompleter]):
        self._construction_dir = construction_dir
        self._completer_class = completer_class

    @property
    @abc.abstractmethod
    def _requirement_to_create(self) -> Union[Path, None]:
        pass

    def create(self):
        if self._requirement_to_create:
            return self._completer_class(
                construction_dir=self._construction_dir)


class WheelCompleterDispatch(CompleterDispatch):
    def __init__(self, construction_dir: cdn.ConstructionDir):
        super().__init__(construction_dir=construction_dir,
                         completer_class=sbn.SrepkgWheelCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._construction_dir.orig_pkg_src_summary.src_for_srepkg_wheel


class SdistCompleterDispatch(CompleterDispatch):
    def __init__(self, construction_dir: cdn.ConstructionDir):
        super().__init__(construction_dir=construction_dir,
                         completer_class=sbn.SrepkgSdistCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._construction_dir.orig_pkg_src_summary.src_for_srepkg_sdist


class SrepkgBuilderBuilder:

    def __init__(self, service_registry: sr.ServiceRegistry):
        self._service_registry = service_registry
        self._construction_dir = service_registry.get_service(
            sr.ServiceObjectID.CONSTRUCTION_DIR)

    def create(self):

        completers = {
            sr.ServiceObjectID.SDIST_COMPLETER:
                SdistCompleterDispatch(construction_dir=self._construction_dir)
                .create(),
            sr.ServiceObjectID.WHEEL_COMPLETER:
                WheelCompleterDispatch(construction_dir=self._construction_dir)
                .create()
        }

        non_null_completers = {key: value for (key, value) in
                               completers.items() if value is not None}

        srepkg_builder = sbn.SrepkgBuilder(
            construction_dir=self._construction_dir,
            srepkg_completers=[value for (key, value) in
                               non_null_completers.items()])

        self._service_registry.register(
            {
                **non_null_completers,
                **{sr.ServiceObjectID.BUILDER: srepkg_builder}
            })

        return srepkg_builder


class ServiceBuilder(re_new_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: nds.SrepkgCommand):
        self._srepkg_command = srepkg_command
        self._service_registry = sr.ServiceRegistry()

    def create_orig_src_preparer(self) -> re_new_int.OrigSrcPreparerInterface:
        osb_builder = OrigSrcPreparerBuilder(
            construction_dir_command=self._srepkg_command.construction_dir,
            orig_pkg_ref_command=self._srepkg_command.orig_pkg_ref,
            srepkg_name_command=self._srepkg_command.srepkg_name,
            service_registry=self._service_registry)
        return osb_builder.create()

    def create_srepkg_builder(self) -> re_new_int.SrepkgBuilderInterface:
        srepkg_builder_builder = SrepkgBuilderBuilder(self._service_registry)
        return srepkg_builder_builder.create()
