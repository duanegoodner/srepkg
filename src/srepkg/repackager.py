import abc
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
import srepkg.shared_data_structures.named_tuples as nt
import srepkg.path_calculator as pc
import srepkg.orig_pkg_inspector as pi
import srepkg.srepkg_builder as sb
from srepkg.srepkg_construction_specs import SrepkgConstructionSpecs


class _Repackager(abc.ABC):
    def __init__(
        self,
        orig_pkg_ref: str,
        srepkg_name: str = None,
        construction_dir: str = None,
        dist_out_dir: str = None,
    ):
        self._orig_pkg_ref = orig_pkg_ref
        self._srepkg_name = srepkg_name
        self._srepkg_temp_dir = None
        if not construction_dir:
            self._srepkg_temp_dir = tempfile.TemporaryDirectory()
            self._construction_dir = Path(self._srepkg_temp_dir.name)
        else:
            self._construction_dir = Path(construction_dir)
        if dist_out_dir:
            self._dist_out_dir = Path(dist_out_dir)
        else:
            self._dist_out_dir = Path.cwd()

    def _cleanup_srepkg_temp_dir(self):
        if self._srepkg_temp_dir:
            self._srepkg_temp_dir.cleanup()

    def _repackage_local(self, orig_pkg: Path):
        print(f"Repackaging {orig_pkg.name}")

        orig_pkg_info = pi.SrcCodeInspector(orig_pkg).get_orig_pkg_info()

        builder_src_paths, builder_dest_paths = pc.SrepkgBuilderPathsCalculator(
            orig_pkg_info.pkg_name, self._construction_dir, self._srepkg_name
        ).calc_builder_paths()

        task_builder_info = nt.TaskBuilderInfo(
            orig_pkg_info=orig_pkg_info,
            src_paths=builder_src_paths,
            repkg_paths=builder_dest_paths,
            dist_out_dir=self._dist_out_dir
        )

        task_catalog = sb.TaskCatalog(task_builder_info)
        construction_specs = SrepkgConstructionSpecs().sdist_procedure
        # task_catalog = task_builder.task_catalog
        # ordered_tasks = sb.TaskOrderArranger(task_catalog).arrange_tasks()
        sb.SrepkgBuilder(task_catalog=task_catalog,
                         task_order=construction_specs).build()

        self._cleanup_srepkg_temp_dir()

    @abc.abstractmethod
    def repackage(self):
        pass


class _LocalRepackager(_Repackager):
    def repackage(self):
        self._repackage_local(Path(self._orig_pkg_ref))


class _RemoteRepackager(_Repackager):
    def _download_archive(self, archive_dir: tempfile.TemporaryDirectory):
        print(f"Downloading {self._orig_pkg_ref}")
        subprocess.call(
            [
                "pip",
                "download",
                "--dest",
                archive_dir.name,
                self._orig_pkg_ref,
                "--no-binary",
                ":all:",
                "--no-deps",
                "--quiet",
            ]
        )

    @staticmethod
    def _extract_archive(
        archive: Path, extract_dir: tempfile.TemporaryDirectory
    ):
        if archive.suffix == ".zip":
            with zipfile.ZipFile(archive, "r") as my_zip:
                my_zip.extractall(Path(extract_dir.name))
        if archive.suffix == ".gz":
            with tarfile.open(archive) as my_tar:
                my_tar.extractall(Path(extract_dir.name))

    def repackage(self):
        archive_dir = tempfile.TemporaryDirectory()
        self._download_archive(archive_dir)

        for file in Path(archive_dir.name).iterdir():
            # if file.suffix in [".gz", ".zip"]:
            extract_dir = tempfile.TemporaryDirectory()
            self._extract_archive(archive=file, extract_dir=extract_dir)

            for package in Path(extract_dir.name).iterdir():
                self._repackage_local(package)
            extract_dir.cleanup()
        archive_dir.cleanup()


class Repackager:
    def __init__(
        self,
        orig_pkg_ref: str,
        construction_dir: str = None,
        srepkg_name: str = None,
        dist_out_dir: str = None,
    ):
        self._orig_pkg_ref = orig_pkg_ref
        self._construction_dir = construction_dir
        self._srepkg_name = srepkg_name
        self._dist_out_dir = dist_out_dir

    @property
    def _is_local(self):
        return (Path(self._orig_pkg_ref).is_dir()) and not all(
            [letter.isalnum() for letter in self._orig_pkg_ref]
        )

    def repackage(self):
        if self._is_local:
            _LocalRepackager(
                self._orig_pkg_ref,
                self._srepkg_name,
                self._construction_dir,
                self._dist_out_dir,
            ).repackage()
        else:
            _RemoteRepackager(
                self._orig_pkg_ref,
                self._srepkg_name,
                self._construction_dir,
                self._dist_out_dir,
            ).repackage()
