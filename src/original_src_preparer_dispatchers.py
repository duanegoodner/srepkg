from functools import singledispatch
from pathlib import Path
import srepkg.dist_provider as opr
import srepkg.construction_dir as cdn
import srepkg.remote_pkg_retriever as rpr


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


def create_retriever_provider_local_src(
        pkg_ref_command: str,
        construction_dir: cdn.ConstructionDir):
    provider = opr.DistProviderFromSrc(
        src_path=Path(pkg_ref_command),
        dest_path=construction_dir.orig_pkg_dists)


def create_retriever_provider_local_dist(
        pkg_ref_command: str,
        construction_dir: cdn.ConstructionDir):
    provider = opr.DistCopyProvider(
        src_path=Path(pkg_ref_command),
        dest_path=construction_dir.orig_pkg_dists
    )


def create_retriever_provider_github(
        pkg_ref_command: str,
        construction_dir: cdn.ConstructionDir):
    retriever = rpr.GithubPkgRetriever(
        pkg_ref=pkg_ref_command)
    provider = opr.DistProviderFromSrc(
        src_path=retriever.copy_dest,
        dest_path=construction_dir.orig_pkg_dists)


def create_retriever_provider_pypi(
        pkg_ref: str,
        copy_dest: Path,
        version: str = None):
    retriever = rpr.PyPIPkgRetriever(
        pkg_ref=pkg_ref,
        copy_dest=copy_dest,
        version=version)

