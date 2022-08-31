import functools
import requests
import subprocess
import tempfile
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename
from pathlib import Path

import srepkg.orig_src_preparer_interfaces as osp_int


class PyPIPkgRetriever(osp_int.RemotePkgRetrieverInterface):
    _pypi_api_base = "https://pypi.org/pypi/{}/json"

    def __init__(self, pkg_ref: str, copy_dest: Path, version: str = None):
        self._pkg_ref = pkg_ref
        self._copy_dest = copy_dest
        self._version = version

    @property
    def _pkg_info_url(self):
        return self._pypi_api_base.format(self._pkg_ref)

    @property
    @functools.lru_cache(maxsize=128, typed=False)
    def _pkg_metadata(self):
        return requests.get(self._pkg_info_url).json()

    @property
    def _version_url_info(self):
        if self._version:
            return self._pkg_metadata["releases"][self._version]
        else:
            return self._pkg_metadata["urls"]

    @property
    def _sdists(self):
        return [dist for dist in self._version_url_info if
                dist["packagetype"] == "sdist"]

    @property
    def _has_sdist(self):
        return len(self._sdists) > 0

    @property
    def _wheels(self):
        return [dist for dist in self._version_url_info if
                dist["packagetype"] == "bdist_wheel"]

    @staticmethod
    def _get_tag(dist_entry: dict):
        name, version, bld, tag = parse_wheel_filename(dist_entry["filename"])
        return list(tag)[0]

    def _is_platform_indep_wheel(self, dist_entry: dict) -> bool:
        # Should we ignore abi when doing this check???
        return self._get_tag(dist_entry).platform == "any"

    @property
    def _platform_indep_wheels(self):
        return [dist for dist in self._wheels if
                self._is_platform_indep_wheel(dist)]

    @property
    def _has_platform_indep_wheel(self):
        return len(self._platform_indep_wheels) > 0

    def _is_platform_specific_wheel(self, dist_entry: dict) -> bool:
        tag = self._get_tag(dist_entry)
        return tag.platform != "any"

    @property
    def _platform_specific_wheels(self):
        return [dist for dist in self._wheels if
                self._is_platform_specific_wheel(dist)]

    @property
    def _platform_specific_wheels_for_cur_sys(self):
        return [
            dist for dist in self._platform_specific_wheels if
            self._get_tag(dist) in list(sys_tags())
        ]

    @property
    def _has_platform_specific_wheel_for_cur_sys(self):
        return len(self._platform_specific_wheels_for_cur_sys) > 0

    @property
    def _dists_to_download(self):
        dists_to_download = []
        if self._has_platform_indep_wheel:
            dists_to_download.append(self._platform_indep_wheels[0])
            return dists_to_download

        if self._has_sdist:
            dists_to_download.append(self._sdists[0])
        if self._has_platform_specific_wheel_for_cur_sys:
            dists_to_download.append(
                self._platform_specific_wheels_for_cur_sys[0])

        return dists_to_download

    def _download(self, dist: dict):
        response = requests.get(dist["url"])
        with (self._copy_dest / dist["filename"]).open(mode="wb") as dist_file:
            dist_file.write(response.content)

    def run(self):
        for dist in self._dists_to_download:
            self._download(dist)


class GithubPkgRetriever(osp_int.RemotePkgRetrieverInterface):

    def __init__(self, pkg_ref: str):
        self._pkg_ref = pkg_ref
        self._temp_dir_obj = tempfile.TemporaryDirectory()

    @property
    def copy_dest(self):
        return Path(self._temp_dir_obj.name)

    def run(self):
        subprocess.run(["git", "clone", self._pkg_ref, self.copy_dest])
