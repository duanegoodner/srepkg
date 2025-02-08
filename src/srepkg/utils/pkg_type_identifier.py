import logging
import requests
import subprocess
import sys
from enum import Enum, auto
from pathlib import Path
from urllib.parse import urlparse
import srepkg.error_handling.error_messages as em
import srepkg.utils.dist_archive_file_tools as cdi
import srepkg.utils.logged_err_detecting_subprocess as leds


class PkgRefType(Enum):
    LOCAL_SRC_NONGIT = auto()
    LOCAL_WHEEL = auto()
    LOCAL_SDIST = auto()
    LOCAL_DIST = auto()
    PYPI_PKG = auto()
    GIT_REPO = auto()
    UNKNOWN = auto()
    MULTIPLE_POSSIBLE = auto()


class PkgRefIdentifier:
    def __init__(self, orig_pkg_ref: str):
        self._orig_pkg_ref = orig_pkg_ref

    def is_local_git_repo(self):
        # choose to NOT wrape this in LoggedErrorDetectingSubprocess b/c we
        # are OK if subprocess return code != 0
        logging.getLogger(__name__).debug(
            "Running git status as subprocess to check if original pkg is a "
            "local git repo"
        )
        p = subprocess.run(
            ["git", "-C", self._orig_pkg_ref, "status"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        for line in p.stdout.strip().split("\n"):
            logging.getLogger(__name__).debug(line)
        for line in p.stderr.strip().split("\n"):
            logging.getLogger(__name__).debug(line)

        return (
            (p.returncode == 0)
            and Path(self._orig_pkg_ref).is_dir()
            and (
                ".git"
                in [
                    item.name
                    for item in list(Path(self._orig_pkg_ref).iterdir())
                ]
            )
        )

    def is_local_src_non_git(self):
        return Path(self._orig_pkg_ref).is_dir() and (
            not self.is_local_git_repo()
        )

    def is_local_wheel(self):
        return (
            (not Path(self._orig_pkg_ref).is_dir())
            and Path(self._orig_pkg_ref).exists()
            and (
                cdi.ArchiveIdentifier().id_file_type(Path(self._orig_pkg_ref))
                == cdi.ArchiveFileType.WHL
            )
        )

    def is_local_sdist(self):
        return (
            (not Path(self._orig_pkg_ref).is_dir())
            and Path(self._orig_pkg_ref).exists()
            and (
                cdi.ArchiveIdentifier().id_file_type(Path(self._orig_pkg_ref))
                != cdi.ArchiveFileType.UNKNOWN
            )
            and (Path(self._orig_pkg_ref).suffix != ".whl")
        )

    def is_pypi_pkg(self):
        response = requests.get(
            "https://pypi.python.org/pypi/{}/json".format(self._orig_pkg_ref)
        )
        return response.status_code == 200

    def is_github_repo(self):
        url_parsed_ref = urlparse(self._orig_pkg_ref)
        return url_parsed_ref.netloc == "github.com" and (
            len(url_parsed_ref.path.split("/")) > 1
        )

    def is_git_repo(self):
        return self.is_local_git_repo() or self.is_github_repo()

    def _check_all_types(self):
        return {
            # PkgRefType.LOCAL_SRC_GIT: self.is_local_git_repo(),
            PkgRefType.LOCAL_SRC_NONGIT: self.is_local_src_non_git(),
            PkgRefType.LOCAL_SDIST: self.is_local_sdist(),
            PkgRefType.LOCAL_WHEEL: self.is_local_wheel(),
            PkgRefType.PYPI_PKG: self.is_pypi_pkg(),
            PkgRefType.GIT_REPO: self.is_git_repo(),
        }

    def identify(self) -> PkgRefType:
        pkg_check_results = self._check_all_types()
        matching_items = [
            item[0] for item in pkg_check_results.items() if item[1] is True
        ]
        num_matches = len(matching_items)

        if num_matches == 0:
            return PkgRefType.UNKNOWN
            # sys.exit(em.PkgIdentifierError.PkgNotFound.msg)

        if num_matches > 1:
            return PkgRefType.MULTIPLE_POSSIBLE
            # sys.exit(em.PkgIdentifierError.MultiplePotentialPackages.msg)

        return matching_items[0]

    def identify_for_osp_dispatch(self):
        gen_pkg_ref_id = self.identify()
        if (gen_pkg_ref_id == PkgRefType.LOCAL_SDIST) or (
            gen_pkg_ref_id == PkgRefType.LOCAL_WHEEL
        ):
            return PkgRefType.LOCAL_DIST
        return gen_pkg_ref_id
