import sys
import requests
from functools import singledispatchmethod
from pathlib import Path
from enum import Enum, auto
from typing import Callable,NamedTuple, Union
from urllib.parse import urlparse

import srepkg.error_handling.error_messages as em

import srepkg.construction_dir_new as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.remote_pkg_retriever as rpr

import srepkg.repackager_new_interfaces as re_new_int

import srepkg.shared_data_structures.new_data_structures as nds

import srepkg.utils.compressed_file_identifier as cdi


class ConstructionDirBuilder:

    @singledispatchmethod
    def create(self, arg) -> cdn.GenConstructionDir:
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


class PkgRefType(Enum):
    LOCAL_SRC = auto()
    LOCAL_WHEEL = auto()
    LOCAL_SDIST = auto()
    PYPI_PKG = auto()
    GITHUB_REPO = auto()


class PkgTypeIdentifier:
    def __init__(self, orig_pkg_ref: str):
        self._orig_pkg_ref = orig_pkg_ref

    def _is_local(self):
        return Path(self._orig_pkg_ref).exists()

    def _is_local_src(self):
        return Path(self._orig_pkg_ref).is_dir()

    def _is_local_wheel(self):
        return (not Path(self._orig_pkg_ref).is_dir()) and \
               Path(self._orig_pkg_ref).exists and \
               (Path(self._orig_pkg_ref).suffix == '.whl') and \
               (cdi.CompressedFileIdentifier().identify_compression_type(Path(
                   self._orig_pkg_ref)) == cdi.ArchiveFileType.ZIP)

    def _is_local_sdist(self):
        return (not Path(self._orig_pkg_ref).is_dir()) and \
               Path(self._orig_pkg_ref).exists and \
               (cdi.CompressedFileIdentifier()
                .identify_compression_type(Path(self._orig_pkg_ref)) !=
                cdi.ArchiveFileType.UNKNOWN) and \
               (Path(self._orig_pkg_ref).suffix != '.whl')

    def _is_pypi_pkg(self):
        response = requests.get("https://pypi.python.org/pypi/{}/json"
                                .format(self._orig_pkg_ref))
        return response.status_code == 200

    def _is_github_repo(self):
        url_parsed_ref = urlparse(self._orig_pkg_ref)
        return url_parsed_ref.netloc == 'github.com' and \
            (len(url_parsed_ref.path.split('/')) > 1)

    def _check_all_types(self):
        return {
            PkgRefType.LOCAL_SRC: self._is_local_src(),
            PkgRefType.LOCAL_SDIST: self._is_local_sdist(),
            PkgRefType.LOCAL_WHEEL: self._is_local_wheel(),
            PkgRefType.PYPI_PKG: self._is_pypi_pkg(),
            PkgRefType.GITHUB_REPO: self._is_github_repo()
        }

    def get_potential_pkg_type(self) -> PkgRefType:
        pkg_check_results = self._check_all_types()
        matching_items = [
            item[0] for item in pkg_check_results.items() if item[1] is True
        ]
        num_matches = len(matching_items)

        if num_matches == 0:
            sys.exit(em.PkgIdentifierError.PkgNotFound.msg)

        if num_matches > 1:
            sys.exit(em.PkgIdentifierError.MultiplePotentialPackages.msg)

        if num_matches == 1:
            return matching_items[0]


class PkgRefDispatchEntry(NamedTuple):
    retriever: Callable[..., rpr.ConstructedPkgRetriever]
    provider: Callable[..., opr.ConstructedDistProvider]


# class RetrieverBuilder:
#     _dispatch_table = {
#         PkgRefType.LOCAL_SRC: rpr.NullPkgRetriever,
#         PkgRefType.LOCAL_SDIST: rpr.NullPkgRetriever,
#         PkgRefType.LOCAL_WHEEL: rpr.NullPkgRetriever,
#         PkgRefType.PYPI_PKG: rpr.PyPIPkgRetriever,
#         PkgRefType.GITHUB_REPO: rpr.GithubPkgRetriever
#     }
#
#     def __init__(self,
#                  orig_pkg_ref: str,
#                  construction_dir: cdn.GenConstructionDir):
#         self._orig_pkg_ref = orig_pkg_ref
#         self._construction_dir = construction_dir
#
#     def create(self):
#         pkg_ref_type = PkgTypeIdentifier(
#             self._orig_pkg_ref).get_potential_pkg_type()
#         return self._dispatch_table[pkg_ref_type](
#             self._orig_pkg_ref, self._construction_dir)


# class DistProviderBuilder:
#     _dispatch_table = {
#         PkgRefType.LOCAL_SRC: opr.WheelAndSdistProvider,
#         PkgRefType.LOCAL_SDIST: opr.DistCopyProvider,
#         PkgRefType.LOCAL_WHEEL: opr.DistCopyProvider,
#         PkgRefType.PYPI_PKG: opr.NullDistProvider,
#         PkgRefType.GITHUB_REPO: opr.WheelAndSdistProvider
#     }
#
#     def __init__(self, orig_pkg_ref: str,
#                  pkg_receiver: cdn.GenConstructionDir):
#         self._orig_pkg_ref = orig_pkg_ref
#         self._pkg_receiver = pkg_receiver
#
#     def create(self) -> opr.ConstructedDistProvider:
#         pkg_ref_type = PkgTypeIdentifier(
#             self._orig_pkg_ref).get_potential_pkg_type()
#         return self._dispatch_table[pkg_ref_type](
#             self._orig_pkg_ref, self._pkg_receiver)


class ServiceBuilder(re_new_int.ServiceBuilderInterface):

    _pkg_ref_dispatch = {
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

    def __init__(self, srepkg_command: nds.SrepkgCommand):
        self._srepkg_command = srepkg_command

    def create_orig_src_preparer(self) -> osp.OrigSrcPreparer:
        construction_dir_builder = ConstructionDirBuilder()
        construction_dir = construction_dir_builder.create(
            self._srepkg_command.construction_dir)

        pkg_ref_type = PkgTypeIdentifier(
            self._srepkg_command.orig_pkg_ref).get_potential_pkg_type()

        retriever = self._pkg_ref_dispatch[pkg_ref_type].retriever(
            self._srepkg_command.orig_pkg_ref, construction_dir)
        provider = self._pkg_ref_dispatch[pkg_ref_type].provider(
            self._srepkg_command.orig_pkg_ref, construction_dir
        )

        return osp.OrigSrcPreparer(
            retriever=retriever,
            provider=provider,
            receiver=construction_dir
        )
