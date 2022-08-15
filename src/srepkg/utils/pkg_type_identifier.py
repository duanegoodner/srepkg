import requests
import sys
from enum import Enum, auto
from pathlib import Path
from urllib.parse import urlparse
import srepkg.error_handling.error_messages as em
import srepkg.utils.dist_archive_file_tools as cdi


class PkgRefType(Enum):
    LOCAL_SRC = auto()
    LOCAL_WHEEL = auto()
    LOCAL_SDIST = auto()
    PYPI_PKG = auto()
    GITHUB_REPO = auto()


class PkgRefIdentifier:
    def __init__(self, orig_pkg_ref: str):
        self._orig_pkg_ref = orig_pkg_ref

    def is_local(self):
        return Path(self._orig_pkg_ref).exists()

    def is_local_src(self):
        return Path(self._orig_pkg_ref).is_dir()

    def is_local_wheel(self):
        return (not Path(self._orig_pkg_ref).is_dir()) and \
               Path(self._orig_pkg_ref).exists() and \
               (cdi.ArchiveIdentifier().id_file_type(Path(
                   self._orig_pkg_ref)) == cdi.ArchiveFileType.WHL)

    def is_local_sdist(self):
        return (not Path(self._orig_pkg_ref).is_dir()) and \
               Path(self._orig_pkg_ref).exists() and \
               (cdi.ArchiveIdentifier()
                .id_file_type(Path(self._orig_pkg_ref)) !=
                cdi.ArchiveFileType.UNKNOWN) and \
               (Path(self._orig_pkg_ref).suffix != '.whl')

    def is_pypi_pkg(self):
        response = requests.get("https://pypi.python.org/pypi/{}/json"
                                .format(self._orig_pkg_ref))
        return response.status_code == 200

    def is_github_repo(self):
        url_parsed_ref = urlparse(self._orig_pkg_ref)
        return url_parsed_ref.netloc == 'github.com' and \
            (len(url_parsed_ref.path.split('/')) > 1)

    def _check_all_types(self):
        return {
            PkgRefType.LOCAL_SRC: self.is_local_src(),
            PkgRefType.LOCAL_SDIST: self.is_local_sdist(),
            PkgRefType.LOCAL_WHEEL: self.is_local_wheel(),
            PkgRefType.PYPI_PKG: self.is_pypi_pkg(),
            PkgRefType.GITHUB_REPO: self.is_github_repo()
        }

    def identify(self) -> PkgRefType:
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
