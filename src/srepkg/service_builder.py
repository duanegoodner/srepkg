import abc
from functools import singledispatchmethod
from pathlib import Path
from typing import Callable, NamedTuple, Type, Union

import srepkg.construction_dir_new as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr
import srepkg.srepkg_builder_new as sbn

import srepkg.repackager_interfaces as re_new_int
import srepkg.srepkg_builder_new_ds_and_int as sb_new_int

import srepkg.shared_data_structures.new_data_structures as nds
from srepkg.utils.pkg_type_identifier import PkgRefType, PkgRefIdentifier

from srepkg.service_registry import ServiceObjectID, SERVICE_REGISTRY


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
                 srepkg_name_command: str = None):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._srepkg_name_command = srepkg_name_command

    @property
    def _construction_dir_dispatch(self):
        return ConstructionDirDispatch()

    @property
    def _retriever_dispatch(self):
        return PkgRetrieverDispatch(pkg_ref_command=self._orig_pkg_ref_command)

    @property
    def _provider_dispatch(self):
        return DistProviderDispatch(pkg_ref_command=self._orig_pkg_ref_command)

    def create(self):
        # ConstructionDirDispatch (w/ @singledispatchmethod) can't take kwargs
        construction_dir = self._construction_dir_dispatch.create(
            self._construction_dir_command, self._srepkg_name_command
        )
        pkg_retriever = self._retriever_dispatch.create(
            construction_dir=construction_dir)
        dist_provider = self._provider_dispatch.create(
            construction_dir=construction_dir)

        orig_src_preparer = osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)

        registry = SERVICE_REGISTRY
        registry.register({
            ServiceObjectID.ORIG_SRC_PREPARER: orig_src_preparer,
            ServiceObjectID.CONSTRUCTION_DIR: construction_dir,
            ServiceObjectID.RETRIEVER: pkg_retriever,
            ServiceObjectID.PROVIDER: dist_provider
        })

        return osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)


class SdistSrcStatus(NamedTuple):
    has_platform_indep_wheel: bool
    has_sdist: bool


class WheelSrcStatus(NamedTuple):
    has_wheel: bool
    has_sdist: bool


class SrepkgDistCompleterDispatch(abc.ABC):

    def __init__(
            self,
            construction_dir: cdn.ConstructionDir,
            completer_class: Type[sbn.SrepkgCompleter]):
        self._construction_dir = construction_dir
        self._completer_class = completer_class

    @property
    @abc.abstractmethod
    def _lookup_key(self) -> NamedTuple:
        pass

    @property
    @abc.abstractmethod
    def _dist_path_lookup_table(self) -> dict[NamedTuple, Path]:
        pass

    def create(self):
        dist_path = self._dist_path_lookup_table[self._lookup_key]
        return self._completer_class(
            construction_dir=self._construction_dir)


class SrepkgWheelCompleterDispatch(SrepkgDistCompleterDispatch):

    @property
    def _lookup_key(self) -> WheelSrcStatus:
        return WheelSrcStatus(
            has_wheel=self._construction_dir.orig_pkg_src_summary.has_wheel,
            has_sdist=self._construction_dir.orig_pkg_src_summary.has_sdist
        )

    @property
    def _dist_path_lookup_table(self) -> dict[WheelSrcStatus, Path]:
        src_summary = self._construction_dir.orig_pkg_src_summary

        return {
            WheelSrcStatus(has_wheel=True, has_sdist=True):
                src_summary.wheel_path,
            WheelSrcStatus(has_wheel=True, has_sdist=False):
                src_summary.wheel_path,
            WheelSrcStatus(has_wheel=False, has_sdist=True):
                src_summary.sdist_path,
            WheelSrcStatus(has_wheel=False, has_sdist=False):
                None
        }


class SrepkgSdistCompleterDispatch(SrepkgDistCompleterDispatch):

    @property
    def _lookup_key(self) -> SdistSrcStatus:
        return SdistSrcStatus(
            has_platform_indep_wheel=self._construction_dir
                .orig_pkg_src_summary.has_wheel,
            has_sdist=self._construction_dir.orig_pkg_src_summary.has_sdist)

    @property
    def _dist_path_lookup_table(self) -> dict[SdistSrcStatus, Path]:
        src_summary = self._construction_dir.orig_pkg_src_summary
        return {
            SdistSrcStatus(has_platform_indep_wheel=True, has_sdist=True):
                src_summary.wheel_path,
            SdistSrcStatus(has_platform_indep_wheel=True, has_sdist=False):
                src_summary.wheel_path,
            SdistSrcStatus(has_platform_indep_wheel=False, has_sdist=True):
                src_summary.sdist_path,
            SdistSrcStatus(has_platform_indep_wheel=False, has_sdist=False):
                None
        }


class CompleterDispatch2:
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


class WheelCompleterDispatch2(CompleterDispatch2):
    def __init__(self, construction_dir: cdn.ConstructionDir):
        super().__init__(construction_dir=construction_dir,
                         completer_class=sbn.SrepkgWheelCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._construction_dir.orig_pkg_src_summary.src_for_srepkg_wheel


class SdistCompleterDispatch2(CompleterDispatch2):
    def __init__(self, construction_dir: cdn.ConstructionDir):
        super().__init__(construction_dir=construction_dir,
                         completer_class=sbn.SrepkgSdistCompleter)

    @property
    def _requirement_to_create(self) -> Union[Path, None]:
        return self._construction_dir.orig_pkg_src_summary.src_for_srepkg_sdist


class SrepkgBuilderBuilder:

    def __init__(self):
        self._construction_dir = SERVICE_REGISTRY.get_service(
            ServiceObjectID.CONSTRUCTION_DIR)

    def create(self):
        sdist_completer = SdistCompleterDispatch2(
            construction_dir=self._construction_dir,
        ).create()
        wheel_completer = WheelCompleterDispatch2(
            construction_dir=self._construction_dir,
        ).create()

        completers = {
            ServiceObjectID.SDIST_COMPLETER: sdist_completer,
            ServiceObjectID.WHEEL_COMPLETER: wheel_completer
        }

        non_null_completers = {key: value for (key, value) in
                               completers.items() if value is not None}

        srepkg_builder = sbn.SrepkgBuilder(
            construction_dir=self._construction_dir,
            srepkg_completers=[value for (key, value) in
                               non_null_completers.items()])

        SERVICE_REGISTRY.register(
            {
                **non_null_completers,
                **{ServiceObjectID.BUILDER: srepkg_builder}
            })

        return srepkg_builder


class ServiceBuilder(re_new_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: nds.SrepkgCommand):
        self._srepkg_command = srepkg_command
        self._service_registry = SERVICE_REGISTRY

    def create_orig_src_preparer(self) -> re_new_int.OrigSrcPreparerInterface:
        osb_builder = OrigSrcPreparerBuilder(
            construction_dir_command=self._srepkg_command.construction_dir,
            orig_pkg_ref_command=self._srepkg_command.orig_pkg_ref,
            srepkg_name_command=self._srepkg_command.srepkg_name)
        return osb_builder.create()

    def create_srepkg_builder(self) -> re_new_int.SrepkgBuilderInterface:
        srepkg_builder_builder = SrepkgBuilderBuilder()
        return srepkg_builder_builder.create()
