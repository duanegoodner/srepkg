import abc
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
import srepkg.orig_pkg_inspector as opi
import srepkg.path_calculator as pc
import srepkg.srepkg_builder as sb


class _Repackager(abc.ABC):

    def __init__(self, pkg_ref: str, srepkg_name: str = None,
                 srepkg_custom_location: Path = None):
        self._pkg_ref = pkg_ref
        self._srepkg_name = srepkg_name
        self._srepkg_custom_location = srepkg_custom_location

    def _repackage_local(self, orig_pkg: Path):
        orig_pkg_info = opi.OrigPkgInspector(str(orig_pkg)).get_orig_pkg_info()

        srepkg_temp_dir = None

        if self._srepkg_custom_location is None:
            srepkg_temp_dir = tempfile.TemporaryDirectory()
            srepkg_location = Path(srepkg_temp_dir.name)
        else:
            srepkg_location = self._srepkg_custom_location

        builder_src_paths, builder_dest_paths = pc.BuilderPathsCalculator(
            orig_pkg_info, srepkg_location, self._srepkg_name)\
            .calc_builder_paths()

        sb.SrepkgBuilder(orig_pkg_info, builder_src_paths,
                         builder_dest_paths).build_srepkg()

        if srepkg_temp_dir:
            srepkg_temp_dir.cleanup()

    @abc.abstractmethod
    def repackage(self):
        pass


class _LocalRepackager(_Repackager):

    def repackage(self):
        self._repackage_local(Path(self._pkg_ref))


class _RemoteRepackager(_Repackager):

    def _download_archive(self, archive_dir: tempfile.TemporaryDirectory):
        subprocess.call([
            'pip',
            'download',
            '-v',
            '--dest',
            archive_dir.name,
            self._pkg_ref,
            '--no-binary',
            ':all:',
            '--no-deps',
            '--quiet'
        ])

    @staticmethod
    def _extract_archive(
            archive: Path,
            extract_dir: tempfile.TemporaryDirectory):
        if archive.suffix == '.zip':
            with zipfile.ZipFile(archive, 'r') as my_zip:
                my_zip.extractall(Path(extract_dir.name))
        if archive.suffix == '.gz':
            with tarfile.open(archive) as my_tar:
                my_tar.extractall(Path(extract_dir.name))

    def repackage(self):
        archive_dir = tempfile.TemporaryDirectory()
        self._download_archive(archive_dir)

        for file in Path(archive_dir.name).iterdir():
            if file.suffix in ['.gz', '.zip']:
                extract_dir = tempfile.TemporaryDirectory()
                self._extract_archive(archive=file, extract_dir=extract_dir)

                for package in Path(extract_dir.name).iterdir():
                    self._repackage_local(package)
                extract_dir.cleanup()
        archive_dir.cleanup()


class Repackager:
    def __init__(self, pkg_ref: str, srepkg_name: str = None,
                 srepkg_location: Path = None):
        self._pkg_ref = pkg_ref
        self._srepkg_name = srepkg_name
        self._srepkg_location = srepkg_location

    @property
    def _is_local(self):
        return (Path(self._pkg_ref).is_dir()) and\
               not all([letter.isalnum for letter in self._pkg_ref])

    def repackage(self):
        if self._is_local:
            _LocalRepackager(
                self._pkg_ref,
                self._srepkg_name,
                self._srepkg_location
            ).repackage()
        else:
            _RemoteRepackager(
                self._pkg_ref,
                self._srepkg_name,
                self._srepkg_location
            ).repackage()


# def repackage_local(orig_pkg: str, srepkg_name: str):
#
#     orig_pkg_info = opi.OrigPkgInspector(orig_pkg).get_orig_pkg_info()
#
#     builder_src_paths, builder_dest_paths = pc.BuilderPathsCalculator(
#         orig_pkg_info, srepkg_name).calc_builder_paths()
#
#     sb.SrepkgBuilder(orig_pkg_info, builder_src_paths,
#                      builder_dest_paths).build_srepkg()







