"""
Contains classes for generating appropriate ServiceBuilder based on a SrepkgCommand.
"""

import sys
from functools import singledispatch
from pathlib import Path
from typing import List, Type, Union, Dict, Callable

import srepkg.construction_dir as cdn
import srepkg.dist_provider as opr
import srepkg.error_handling.custom_exceptions as ce
import srepkg.error_handling.error_messages as em
import srepkg.orig_src_preparer as osp
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.remote_pkg_retriever as rpr
import srepkg.srepkg_builder as sbn

import srepkg.repackager_data_structs as rep_ds
import srepkg.repackager_interfaces as rep_int

from srepkg.utils.pkg_type_identifier import PkgRefType, PkgRefIdentifier


@singledispatch
def create_construction_dir(
    construction_dir_command, srepkg_name_command: str = None
) -> cdn.ConstructionDir:
    """
    Enables function overloading based on type(construction_dir_command) and
    Args:
        construction_dir_command:
        srepkg_name_command: optional command passed when using custom name
        for a re-packaged package.
    Returns:

    """
    raise NotImplementedError


@create_construction_dir.register(type(None))
def _(construction_dir_command, srepkg_name_command: str = None):
    return cdn.TempConstructionDir(srepkg_name_command=srepkg_name_command)


@create_construction_dir.register(str)
def _(construction_dir_command, srepkg_name_command: str = None):
    return cdn.CustomConstructionDir(
        construction_dir_command=Path(construction_dir_command),
        srepkg_name_command=srepkg_name_command,
    )


@create_construction_dir.register(Path)
def _(construction_dir_command, srepkg_name_command: str = None):
    return cdn.CustomConstructionDir(
        construction_dir_command=construction_dir_command,
        srepkg_name_command=srepkg_name_command,
    )


class RetrieverProviderDispatch:
    """
    Determines which implementation of DistProviderInterface is needed,
    and (if necessary) which implementation of RemotePkgRetrieverInterface is needed.
    """

    def __init__(
        self,
        pkg_ref_command: str,
        construction_dir: cdn.ConstructionDir,
        version_command: str = None,
        git_ref: str = None,
    ):
        """

        Args:
            pkg_ref_command: package identifier (e.g. PyPI name, GitHub repo)
            construction_dir: object with path and methods management methods for build dir
            version_command: PyPI version
            git_ref: git commit or tag
        """
        self._pkg_ref_command = pkg_ref_command
        self._construction_dir = construction_dir
        self._version_command = version_command
        self._git_ref = git_ref

    def _create_for_local_src_nongit(
        self,
    ) -> List[osp_int.DistProviderInterface]:
        provider = opr.DistProviderFromSrc(
            src_path=Path(self._pkg_ref_command),
            dest_path=self._construction_dir.orig_pkg_dists,
        )
        return [provider]

    def _create_for_local_dist(self) -> List[osp_int.DistProviderInterface]:
        provider = opr.DistCopyProvider(
            src_path=Path(self._pkg_ref_command),
            dest_path=self._construction_dir.orig_pkg_dists,
        )
        return [provider]

    def _create_for_git_repo(self):
        retriever = rpr.GithubPkgRetriever(pkg_ref=self._pkg_ref_command)
        # provider = opr.DistProviderFromSrc(
        #     src_path=retriever.copy_dest,
        #     dest_path=self._construction_dir.orig_pkg_dists)
        provider = opr.DistProviderFromGitRepo(
            src_path=retriever.copy_dest,
            dest_path=self._construction_dir.orig_pkg_dists,
            git_ref=self._git_ref,
            version_command=self._version_command,
        )
        return [retriever, provider]

    def _create_for_pypi(self):
        retriever = rpr.PyPIPkgRetriever(
            pkg_ref=self._pkg_ref_command,
            copy_dest=self._construction_dir.orig_pkg_dists,
            version_command=self._version_command,
        )
        return [retriever]

    @property
    def _dispatch_table(self) -> Dict[PkgRefType, Callable]:
        return {
            # PkgRefType.LOCAL_SRC_GIT: self._create_for_local_src_git,
            PkgRefType.LOCAL_SRC_NONGIT: self._create_for_local_src_nongit,
            PkgRefType.LOCAL_DIST: self._create_for_local_dist,
            PkgRefType.GIT_REPO: self._create_for_git_repo,
            PkgRefType.PYPI_PKG: self._create_for_pypi,
        }

    def create(self) -> List:
        """

        Returns:
            1 or 2 element List with instance of a DistProviderInterface
            and/or a RemotePkgRetrieverInterface
        """
        pkg_ref_type = PkgRefIdentifier(
            self._pkg_ref_command
        ).identify_for_osp_dispatch()

        if pkg_ref_type == PkgRefType.UNKNOWN:
            sys.exit(em.PkgIdentifierError.PkgNotFound.msg)

        if pkg_ref_type == PkgRefType.MULTIPLE_POSSIBLE:
            sys.exit(em.PkgIdentifierError.MultiplePotentialPackages.msg)

        if self._git_ref and not pkg_ref_type == PkgRefType.GIT_REPO:
            raise ce.UnusableGitCommitRef(self._git_ref)

        if self._version_command and not pkg_ref_type == PkgRefType.PYPI_PKG:
            raise ce.UnusableVersionArgument(self._version_command)

        return self._dispatch_table[pkg_ref_type]()


class OrigSrcPreparerBuilder:

    def __init__(
        self,
        construction_dir_command: Union[str, None],
        orig_pkg_ref_command: str,
        srepkg_name_command: str = None,
        version_command: str = None,
        git_ref_command: str = None,
    ):
        self._construction_dir_command = construction_dir_command
        self._orig_pkg_ref_command = orig_pkg_ref_command
        self._srepkg_name_command = srepkg_name_command
        self._version_command = version_command
        self._git_ref_command = git_ref_command
        self._construction_dir_dispatch = create_construction_dir

    def create(self):
        construction_dir = self._construction_dir_dispatch(
            self._construction_dir_command, self._srepkg_name_command
        )

        retriever_provider = RetrieverProviderDispatch(
            pkg_ref_command=self._orig_pkg_ref_command,
            construction_dir=construction_dir,
            version_command=self._version_command,
            git_ref=self._git_ref_command,
        ).create()

        return osp.OrigSrcPreparer(
            retriever_provider=retriever_provider, receiver=construction_dir
        )


class SrepkgBuilderBuilder:

    def __init__(
        self,
        output_dir_command: Union[str, None],
        construction_dir_summary: rep_ds.ConstructionDirSummary,
    ):
        self._construction_dir_summary = construction_dir_summary
        if output_dir_command is None:
            output_dir_command = str(Path.cwd())
        self._output_dir = output_dir_command

    @property
    def _completer_dispatch(
        self,
    ) -> Dict[Type[sbn.SrepkgCompleter], Union[Path, None]]:
        return {
            sbn.SrepkgWheelCompleter: self._construction_dir_summary.src_for_srepkg_wheel,
            sbn.SrepkgSdistCompleter: self._construction_dir_summary.src_for_srepkg_sdist,
        }

    def create(self):

        completers = []
        for constructor, src_path in self._completer_dispatch.items():
            if src_path is not None:
                completers.append(
                    constructor(
                        orig_pkg_summary=self._construction_dir_summary,
                        dist_out_dir=Path(self._output_dir),
                    )
                )

        srepkg_builder = sbn.SrepkgBuilder(
            construction_dir_summary=self._construction_dir_summary,
            srepkg_completers=completers,
            output_dir=(
                Path(self._output_dir) if self._output_dir else Path.cwd()
            ),
        )

        return srepkg_builder


class ServiceBuilder(rep_int.ServiceBuilderInterface):
    """
    Contains methods for generating instances of appropriate
    OrigSrcPreparerInterface and SrepkgBuilderInterface for a SrepkgCommand
    """

    def __init__(self, srepkg_command: rep_int.SrepkgCommand):
        """

        Args:
            srepkg_command (): a SrepkgCommand object, typically built from
            command line arguments (but can be built my args passed to
            srepkg.main() during testing).
        """
        self._srepkg_command = srepkg_command

    def create_orig_src_preparer(self) -> rep_int.OrigSrcPreparerInterface:
        """
        Creates instance of class that implements OrigSrcPreparerInterface.
        Specific concrete class used depends on attributes of SrepkgCommand.

        Returns:
            Instance of a class that implements OrigSrcPreparerInterface.

        """
        osp_builder = OrigSrcPreparerBuilder(
            construction_dir_command=self._srepkg_command.construction_dir,
            orig_pkg_ref_command=self._srepkg_command.orig_pkg_ref,
            srepkg_name_command=self._srepkg_command.srepkg_name,
            git_ref_command=self._srepkg_command.git_ref,
            version_command=self._srepkg_command.pypi_version,
        )
        return osp_builder.create()

    def create_srepkg_builder(
        self, construction_dir_summary: rep_ds.ConstructionDirSummary
    ) -> rep_int.SrepkgBuilderInterface:
        """
        Creates instance of class that implements SrepkgBuilderInterface.
        Args:
            construction_dir_summary ():

        Returns:

        """
        srepkg_builder_builder = SrepkgBuilderBuilder(
            output_dir_command=self._srepkg_command.dist_out_dir,
            construction_dir_summary=construction_dir_summary,
        )
        return srepkg_builder_builder.create()
