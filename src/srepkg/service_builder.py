import abc
from functools import singledispatch
from pathlib import Path
from typing import List, Type, Union

import srepkg.construction_dir as cdn
import srepkg.dist_provider as opr
import srepkg.orig_src_preparer as osp
import srepkg.orig_src_preparer_interfaces as osp_int
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


class RetrieverProviderDispatch:

    def __init__(self,
                 pkg_ref_command: str,
                 construction_dir: cdn.ConstructionDir,
                 version_command: str = None):
        self._pkg_ref_command = pkg_ref_command
        self._construction_dir = construction_dir
        self._version = version_command

    def _create_for_local_src(self) -> List[osp_int.DistProviderInterface]:
        provider = opr.DistProviderFromSrc(
            src_path=Path(self._pkg_ref_command),
            dest_path=self._construction_dir.orig_pkg_dists)
        return [provider]

    def _create_for_local_dist(self) -> List[osp_int.DistProviderInterface]:
        provider = opr.DistCopyProvider(
            src_path=Path(self._pkg_ref_command),
            dest_path=self._construction_dir.orig_pkg_dists)
        return [provider]

    def _create_for_github(self):
        retriever = rpr.GithubPkgRetriever(
            pkg_ref=self._pkg_ref_command)
        provider = opr.DistProviderFromSrc(
            src_path=retriever.copy_dest,
            dest_path=self._construction_dir.orig_pkg_dists)
        return [retriever, provider]

    def _create_for_pypi(self):
        retriever = rpr.PyPIPkgRetriever(
            pkg_ref=self._pkg_ref_command,
            copy_dest=self._construction_dir.orig_pkg_dists,
            version=self._version)
        return [retriever]

    @property
    def _dispatch_table(self):
        return {
            PkgRefType.LOCAL_SRC: self._create_for_local_src,
            PkgRefType.LOCAL_DIST: self._create_for_local_dist,
            PkgRefType.GITHUB_REPO: self._create_for_github,
            PkgRefType.PYPI_PKG: self._create_for_pypi
        }

    def create(self):

        pkg_ref_type = PkgRefIdentifier(self._pkg_ref_command)\
            .identify_for_osp_dispatch()
        return self._dispatch_table[pkg_ref_type]()


class OrigSrcPreparerBuilder:

    def __init__(self,
                 construction_dir_command: Union[str, None],
                 orig_pkg_ref_command: str,
                 srepkg_name_command: str = None,
                 version_command: str = None):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._srepkg_name_command = srepkg_name_command
        self._version_command = version_command
        self._construction_dir_dispatch = create_construction_dir

    def create(self):
        construction_dir = self._construction_dir_dispatch(
            self._construction_dir_command, self._srepkg_name_command)

        retriever_provider = RetrieverProviderDispatch(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir,
            version_command=self._version_command
        ).create()

        return osp.OrigSrcPreparer(
            retriever_provider=retriever_provider,
            receiver=construction_dir)


class SrepkgBuilderBuilder:

    def __init__(
            self,
            output_dir_command: Union[str, None],
            construction_dir_summary: rep_ds.ConstructionDirSummary):
        self._construction_dir_summary = construction_dir_summary
        self._output_dir = output_dir_command

    @property
    def _completer_dispatch(self) ->\
            dict[Type[sbn.SrepkgCompleter], Union[Path, None]]:
        return {
            sbn.SrepkgWheelCompleter:
                self._construction_dir_summary.src_for_srepkg_wheel,
            sbn.SrepkgSdistCompleter:
                self._construction_dir_summary.src_for_srepkg_sdist
        }

    def create(self):

        completers = []
        for constructor, src_path in self._completer_dispatch.items():
            if src_path is not None:
                completers.append(
                    constructor(orig_pkg_summary=self._construction_dir_summary)
                )

        srepkg_builder = sbn.SrepkgBuilder(
            construction_dir_summary=self._construction_dir_summary,
            srepkg_completers=completers,
            output_dir=Path(self._output_dir)
            if self._output_dir else Path.cwd()
        )

        return srepkg_builder


class ServiceBuilder(rep_int.ServiceBuilderInterface):

    def __init__(self, srepkg_command: rep_int.SrepkgCommand):
        self._srepkg_command = srepkg_command

    def create_orig_src_preparer(self) -> rep_int.OrigSrcPreparerInterface:
        osp_builder = OrigSrcPreparerBuilder(
            construction_dir_command=self._srepkg_command.construction_dir,
            orig_pkg_ref_command=self._srepkg_command.orig_pkg_ref,
            srepkg_name_command=self._srepkg_command.srepkg_name)
        return osp_builder.create()

    def create_srepkg_builder(
            self,
            construction_dir_summary: rep_ds.ConstructionDirSummary) \
            -> rep_int.SrepkgBuilderInterface:
        srepkg_builder_builder = SrepkgBuilderBuilder(
            output_dir_command=self._srepkg_command.dist_out_dir,
            construction_dir_summary=construction_dir_summary
        )
        return srepkg_builder_builder.create()
