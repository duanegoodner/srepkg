"""
Contains classes for retrieving packages from remote locations.
"""

import functools
import logging
import requests
import tempfile
from packaging.tags import sys_tags, Tag
from packaging.utils import parse_wheel_filename
from pathlib import Path
from typing import Dict, Any, List

import inner_pkg_installer.yaspin_updater as yu
import srepkg.error_handling.custom_exceptions as ce
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.utils.logged_err_detecting_subprocess as leds


class PyPIPkgRetriever(osp_int.RemotePkgRetrieverInterface):
    """
    Retrieves packages from Python Package Index.
    """
    _pypi_api_base = "https://pypi.org/pypi/{}/json"

    def __init__(
        self, pkg_ref: str, copy_dest: Path, version_command: str = None
    ):
        self._pkg_ref = pkg_ref
        self._copy_dest = copy_dest
        self._version_command = version_command

    @property
    def _pkg_info_url(self) -> str:
        return self._pypi_api_base.format(self._pkg_ref)

    @property
    @functools.lru_cache(maxsize=128, typed=False)
    def _pkg_metadata(self) -> Dict[str, Any]:
        return requests.get(self._pkg_info_url).json()

    @property
    def _version_url_info(self) -> List[Dict[str, Any]]:
        if self._version_command:
            return self._pkg_metadata["releases"][self._version_command]
        else:
            return self._pkg_metadata["urls"]

    @property
    def _sdists(self) -> List[Dict[str, Any]]:
        return [
            dist
            for dist in self._version_url_info
            if dist["packagetype"] == "sdist"
        ]

    @property
    def _has_sdist(self) -> bool:
        return len(self._sdists) > 0

    @property
    def _wheels(self) -> List[Dict[str, Any]]:
        return [
            dist
            for dist in self._version_url_info
            if dist["packagetype"] == "bdist_wheel"
        ]

    @staticmethod
    def _get_tag(dist_entry: dict) -> Tag:
        name, version, bld, tag = parse_wheel_filename(dist_entry["filename"])
        return list(tag)[0]

    def _is_platform_indep_wheel(self, dist_entry: dict) -> bool:
        # Should we ignore abi when doing this check???
        return self._get_tag(dist_entry).platform == "any"

    @property
    def _platform_indep_wheels(self) -> List[Dict[str, Any]]:
        return [
            dist
            for dist in self._wheels
            if self._is_platform_indep_wheel(dist)
        ]

    @property
    def _has_platform_indep_wheel(self) -> bool:
        return len(self._platform_indep_wheels) > 0

    def _is_platform_specific_wheel(self, dist_entry: dict) -> bool:
        tag = self._get_tag(dist_entry)
        return tag.platform != "any"

    @property
    def _platform_specific_wheels(self) -> List[Dict[str, Any]]:
        return [
            dist
            for dist in self._wheels
            if self._is_platform_specific_wheel(dist)
        ]

    @property
    def _platform_specific_wheels_for_cur_sys(self) -> List[Dict[str, Any]]:
        return [
            dist
            for dist in self._platform_specific_wheels
            if self._get_tag(dist) in list(sys_tags())
        ]

    @property
    def _has_platform_specific_wheel_for_cur_sys(self) -> bool:
        return len(self._platform_specific_wheels_for_cur_sys) > 0

    @property
    def _dists_to_download(self) -> List[Dict[str, Any]]:
        dists_to_download = []
        if self._has_platform_indep_wheel:
            dists_to_download.append(self._platform_indep_wheels[0])
            return dists_to_download

        if self._has_sdist:
            dists_to_download.append(self._sdists[0])
        if self._has_platform_specific_wheel_for_cur_sys:
            dists_to_download.append(
                self._platform_specific_wheels_for_cur_sys[0]
            )

        return dists_to_download

    def _download(self, dist: dict) -> None:
        response = requests.get(dist["url"])
        with (self._copy_dest / dist["filename"]).open(mode="wb") as dist_file:
            dist_file.write(response.content)

    def run(self) -> None:

        with yu.yaspin_log_updater(
            msg=f"Retrieving {self._pkg_ref} from Python Packaging Index",
            logger=logging.getLogger(__name__),
        ) as updater:

            for dist in self._dists_to_download:
                self._download(dist)

        downloaded_files = "\n".join(
            [f"\t• {dist['filename']}" for dist in self._dists_to_download]
        )
        post_msg = f"\tDownloaded files:\n{downloaded_files}"
        logging.getLogger(f"std_out.{__name__}").info(post_msg)


class GithubPkgRetriever(osp_int.RemotePkgRetrieverInterface):
    """
    Retrieves packages from Github.
    """

    def __init__(self, pkg_ref: str):
        self._pkg_ref = pkg_ref
        self._temp_dir_obj = tempfile.TemporaryDirectory()

    @property
    def copy_dest(self):
        return Path(self._temp_dir_obj.name)

    def run(self):
        with yu.yaspin_log_updater(
            msg=f"Cloning {self._pkg_ref} into temporary directory",
            logger=logging.getLogger(__name__),
        ) as updater:
            leds.LoggedErrDetectingSubprocess(
                cmd=["git", "clone", self._pkg_ref, self.copy_dest],
                gen_logger_name=__name__,
                std_out_logger_name="std_out",
                std_err_logger_name="std_err",
                default_exception=ce.GitCheckoutError,
            ).run()
