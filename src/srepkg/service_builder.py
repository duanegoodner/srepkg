import abc
from enum import Enum, auto
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Callable, NamedTuple, Union

import srepkg.construction_dir_new as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr
import srepkg.srepkg_builder_new as sbn

import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.repackager_new_interfaces as re_new_int


import srepkg.shared_data_structures.new_data_structures as nds
from srepkg.utils.pkg_type_identifier import PkgRefType, PkgRefIdentifier
from srepkg.utils.thread_safe_singletong import ThreadSafeSingleton


class ConstructionDirDispatch:

    @singledispatchmethod
    def create(self, construction_dir_arg,
               srepkg_name_arg: str = None) -> cdn.ConstructionDir:
        raise NotImplementedError

    @create.register(type(None))
    def _(self, construction_dir_arg, srepkg_name_arg: str = None):
        return cdn.TempConstructionDir(srepkg_name_arg=srepkg_name_arg)

    @create.register(str)
    def _(self, construction_dir_arg, srepkg_name_arg: str = None):
        return cdn.CustomConstructionDir(
            construction_dir_arg=Path(construction_dir_arg),
            srepkg_name_arg=srepkg_name_arg)

    @create.register(Path)
    def _(self, construction_dir_arg, srepkg_name_arg: str = None):
        return cdn.CustomConstructionDir(
            construction_dir_arg=construction_dir_arg,
            srepkg_name_arg=srepkg_name_arg)


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
                 srepkg_name_arg: str = None,
                 ):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._srepkg_name_arg = srepkg_name_arg
        self._construction_dir_dispatch = ConstructionDirDispatch()
        self._retriever_dispatch = PkgRetrieverDispatch()
        self._provider_dispatch = DistProviderDispatch()

    def create(self):
        # ConstructionDirDispatch (w/ @singledispatchmethod) can't take kwargs
        construction_dir = self._construction_dir_dispatch.create(
            self._construction_dir_command, self._srepkg_name_arg)
        pkg_retriever = self._retriever_dispatch.create(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir)
        dist_provider = self._provider_dispatch.create(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir)

        orig_src_preparer = osp.OrigSrcPreparer(
            retriever=pkg_retriever,
            provider=dist_provider,
            receiver=construction_dir)

        registry = ServiceRegistry()
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


class SourceStatus(NamedTuple):
    wheel_is_none_any: bool
    has_sdist: bool


class SrepkgBuilderDispatch:

    @property
    def _dispatch_table(self) -> dict[SourceStatus, Callable]:
        return {
            SourceStatus(wheel_is_none_any=True, has_sdist=True):
                sbn.SdistWheelBuilder,
            SourceStatus(wheel_is_none_any=True, has_sdist=False):
                sbn.WheelWheelBuilder,
            SourceStatus(wheel_is_none_any=False, has_sdist=True):
                sbn.SdistSdistBuilder,
            SourceStatus(wheel_is_none_any=False, has_sdist=False):
                sbn.WheelWheelBuilder
        }

    def create(
            self,
            source_status: SourceStatus,
            construction_dir: osp_int.WritableSrepkgDirInterface):
        return self._dispatch_table[source_status](construction_dir)



class SrepkgBuilderBuilder:

    _builder_dispatch = SrepkgBuilderDispatch()

    def _get_construction_dir_source_status(
            self,
            construction_dir: osp_int.WritableSrepkgDirInterface)\
            -> SourceStatus:
        pass

    def create(self) -> re_new_int.SrepkgBuilderInterface:
        registry = ServiceRegistry()
        construction_dir = registry.get_service(
            ServiceObjectID.CONSTRUCTION_DIR)
        source_status = self._get_construction_dir_source_status(
            construction_dir)
        srepkg_builder = self._builder_dispatch.create(
            source_status=source_status, construction_dir=construction_dir)
        registry.register({ServiceObjectID.BUILDER: srepkg_builder})

        return srepkg_builder


class ServiceObjectID(Enum):
    ORIG_SRC_PREPARER = auto()
    RETRIEVER = auto()
    PROVIDER = auto()
    CONSTRUCTION_DIR = auto()
    BUILDER = auto()


class ServiceRegistry(ThreadSafeSingleton):

    def __init__(self, registry: dict[ServiceObjectID, Any] = None):
        if registry is None:
            registry = {}
        self._registry = registry

    def register(self, new_items: dict[ServiceObjectID, object]):
        for item in new_items:
            if item in self._registry:
                raise DuplicateServiceObjectID(item)
        self._registry.update(new_items)

    def get_service(self, object_id: ServiceObjectID):
        try:
            return self._registry[object_id]
        except KeyError:
            raise UnregisteredServiceObjectID(object_id)


class DuplicateServiceObjectID(Exception):
    def __init__(
            self,
            service_object_id: ServiceObjectID,
            msg="Service object ID already entered in ServiceRegistry"):
        self._service_object_id = service_object_id
        self._msg = msg

    def __str__(self):
        return f"{str(self._service_object_id)} -> {self._msg}"


class UnregisteredServiceObjectID(Exception):
    def __init__(
            self,
            service_object_id: ServiceObjectID,
            msg="Object ID not found in service registry"):
        self._service_object_id = service_object_id
        self._msg = msg

    def __str__(self):
        return f"{str(self._service_object_id)} -> {self._msg}"


class ServiceBuilder(re_new_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: nds.SrepkgCommand):
        self._srepkg_command = srepkg_command
        self._osp_builder = OrigSrcPreparerBuilder(
            construction_dir_command=srepkg_command.construction_dir,
            orig_pkg_ref_command=srepkg_command.orig_pkg_ref,
            srepkg_name_arg=srepkg_command.srepkg_name)
        self._srepkg_build_builder = SrepkgBuilderBuilder()

    def create_orig_src_preparer(self) -> re_new_int.OrigSrcPreparerInterface:
        return self._osp_builder.create()

    def create_srepkg_builder(self) -> re_new_int.SrepkgBuilderInterface:
        return self._srepkg_build_builder.create()

