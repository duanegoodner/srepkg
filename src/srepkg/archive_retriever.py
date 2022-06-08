import abc
import git
import sys
import warnings

import re

import requests
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
import uuid

from enum import Enum
from packaging import version
from pathlib import Path
from typing import List, Callable, NamedTuple
from urllib.parse import urlparse

import custom_datatypes as cd


class ArchiveRetrieverError(cd.nt.ErrorMsg, Enum):
    DefaultReleaseInfoNotFound = cd.nt.ErrorMsg(
        msg='Default release info not found in PyPI. srepkg will attempt to'
            'obtain info for latest release')
    NoTarGzFound = cd.nt.ErrorMsg(
        msg='.tar.gz archive not in PyPI for this version')
    NoGitCommitIdentifyingInfo = cd.nt.ErrorMsg(
        msg='No Git branch name found, and no commit SHA found. Need at least '
            'one of these.')
    BranchNameNotFound = cd.nt.ErrorMsg(msg='Input branch name not found')
    CommitSHANotFound = cd.nt.ErrorMsg(msg='Input SHA value not found')
    BranchNameSHAMismatch = cd.nt.ErrorMsg(
        msg='Commit for provided SHA does not belong to specified branch')


class ValidationCondition(NamedTuple):
    criteria: bool
    error_on_fail: ArchiveRetrieverError


class NoTarGzForVersion(Exception):
    def __init__(
            self,
            version_identifier: str,
            msg=ArchiveRetrieverError.NoTarGzFound.msg):
        self._version_identifier = version_identifier
        self._msg = msg

    def __str__(self):
        return f'{self._version_identifier} -> {self._msg}'


class _ArchiveRetriever(abc.ABC):

    def __init__(self, pkg_ref: str, archive_dir: Path,
                 archive_filename: str = uuid.uuid4().hex):
        self._pkg_ref = pkg_ref
        self._archive_dir = archive_dir
        self._archive_filename = archive_filename

    # TODO method and/or data member for metadata

    @abc.abstractmethod
    def retrieve_archive(self):
        pass


class _LocalCommitArchiveRetriever(_ArchiveRetriever):

    def __init__(
            self,
            pkg_ref: str,
            archive_dir: Path,
            archive_filename: str = uuid.uuid4().hex,
            # repo: git.repo.base.Repo = git.Repo(str(Path.cwd())),
            branch: str = '',
            commit_sha: str = ''):
        super().__init__(pkg_ref, archive_dir, archive_filename)
        self._repo = git.Repo(pkg_ref)
        self._branch = branch
        self._commit_sha = commit_sha

    @property
    def _branch_names(self) -> List[str]:
        return [head.name for head in self._repo.heads]

    def _commits_for_branch(self, branch_name: str):
        return [commit.hexsha for commit in
                list(self._repo.iter_commits(branch_name))]

    @property
    def _all_commits(self) -> dict[str, List[str]]:
        return {branch_name: self._commits_for_branch(branch_name) for
                branch_name in self._branch_names}

    @property
    def _identifier_provided(self) -> ValidationCondition:
        return ValidationCondition(
            criteria=bool(self._branch) or bool(self._commit_sha),
            error_on_fail=ArchiveRetrieverError.NoGitCommitIdentifyingInfo)

    @property
    def _valid_input_branch(self) -> ValidationCondition:
        return ValidationCondition(
            criteria=
            (not self._branch) or
            (self._branch in [head.name for head in self._repo.heads]),
            error_on_fail=ArchiveRetrieverError.BranchNameNotFound)

    @property
    def _valid_input_sha(self) -> ValidationCondition:

        return ValidationCondition(
            criteria=(not self._commit_sha) or
            (self._commit_sha in set().union(
                *list(self._all_commits.values()))),
            error_on_fail=ArchiveRetrieverError.CommitSHANotFound)

    @property
    def _branch_and_sha_consistent(self) -> ValidationCondition:

        return ValidationCondition(
            criteria=(not self._branch) or (not self._commit_sha) or
                     (self._commit_sha in self._all_commits[self._branch]),
            error_on_fail=ArchiveRetrieverError.BranchNameSHAMismatch)

    def _validate_identifiers(self):

        # use getter functions for Validation Conditions instead of just
        # defining here so we have option for intermediate variables if
        # criteria function is complicated

        validation_conditions = [
            self._identifier_provided,
            self._valid_input_branch,
            self._valid_input_sha,
            self._branch_and_sha_consistent
        ]

        for condition in validation_conditions:
            if not condition.criteria:
                sys.exit(condition.error_on_fail.msg)

    def retrieve_archive(self):
        pass  # implementation TBD


class _RemoteArchiveRetriever(_ArchiveRetriever, abc.ABC):
    def __init__(self, pkg_ref: str, archive_dir: Path,
                 archive_filename: str = uuid.uuid4().hex,
                 archive_url: str = ''):
        super().__init__(pkg_ref, archive_dir, archive_filename)

        self._archive_url = archive_url

    @abc.abstractmethod
    def _set_archive_url(self):
        pass

    def _request_archive(self) -> requests.models.Response:
        return requests.get(self._archive_url)

    def _write_archive(self, content: bytes):
        with (self._archive_dir / self._archive_filename).open(mode='wb') \
                as archive_file:
            archive_file.write(content)

        return self._archive_dir / self._archive_filename

    def _get_extra_data_from_archive_response(
            self, archive_response: requests.models.Response) -> None:
        pass

    def retrieve_archive(self):
        self._set_archive_url()
        archive_response = self._request_archive()
        self._get_extra_data_from_archive_response(archive_response)

        return self._write_archive(archive_response.content)


class _GithubArchiveRetriever(_RemoteArchiveRetriever):
    _github_api_base = 'https://api.github.com/repos/'

    @property
    def _identifiers(self):
        # a 1 or 2 element list. 1st is 'user/repo_name'
        # 2nd (if present) is a commit ref
        return urlparse(self._pkg_ref).path.split('@')

    def _set_archive_url(self):
        archive_url = self._github_api_base + self._identifiers[0] + '/zipball'
        if len(self._identifiers) > 1:
            archive_url += '/' + self._identifiers[1]
        self._archive_url = archive_url

    def _get_extra_data_from_archive_response(
            self, archive_response: requests.models.Response):
        self._archive_filename = archive_response \
            .headers['content-disposition'].split('=')[-1]


class _PyPIArchiveRetriever(_RemoteArchiveRetriever):
    _pypi_api_base = 'https://pypi.org/pypi/{}/json'

    def __init__(self, pkg_ref: str, archive_dir: Path,
                 requested_version: str = ''):
        super().__init__(pkg_ref, archive_dir)
        self._requested_version = requested_version

    @property
    def _identifiers(self):
        return [self._pkg_ref, self._requested_version]

    @property
    def _pkg_info_url(self):
        if self._requested_version:
            return self._pypi_api_base.format(
                ''.join([self._pkg_ref, '/', self._requested_version]))
        else:
            return self._pypi_api_base.format(self._pkg_ref)

    def _set_archive_url(self):

        def _extract_extra_info(data_source: any):
            self._archive_filename = data_source['filename']

        package_metadata = requests.get(self._pkg_info_url).json()
        available_urls = package_metadata['urls']
        tar_gz_info = [url_info for url_info in available_urls if
                       Path(url_info['filename']).suffix == '.gz']
        if len(tar_gz_info) == 0:
            sys.exit(ArchiveRetrieverError.NoTarGzFound.msg)

        self._archive_url = tar_gz_info[0]['url']
        _extract_extra_info(tar_gz_info[0])

# class _SrcCodeRetriever(abc.ABC):
#
#     def __init__(self, pkg_ref: str):
#         self._pkg_ref = pkg_ref
#
#     @abc.abstractmethod
#     def get_pkg_src_code(self):
#         pass
#
#
# class _LocalSrcCodeRetriever(_SrcCodeRetriever):
#
#     def get_pkg_src_code(self) -> Path:
#         return Path(self._pkg_ref)
#
#
# class _RemoteSrcCodeRetriever(_SrcCodeRetriever, abc.ABC):
#
#     def __init__(self, pkg_ref: str, archive_dir: Path,
#                  extract_dir: Path):
#         super().__init__(pkg_ref)
#         self._archive_dir = archive_dir
#         self._extract_dir = extract_dir
#
#     @abc.abstractmethod
#     def _get_url(self):
#         pass
#
#     def _download_archive(self):
#         archive_request = requests.get(self._get_url())
#         with Path(self._archive_dir / self._archive_filename).open(mode='wb')\
#                 as archive_file:
#             archive_file.write(archive_request.content)
#
#         return self
#
#     def _extract_archive(self):
#         if self._archive_file.suffix == '.zip':
#             with zipfile.ZipFile(self._archive_file, 'r') as my_zip:
#                 my_zip.extractall(self._extract_dir)
#         if self._archive_file.suffix == '.gz':
#             with tarfile.open(self._archive_file) as my_tar:
#                 my_tar.extractall(self._extract_dir)
#
#         return self
#
#     def get_pkg_src_code(self):
#         self._download_archive()._extract_archive()
#
#         return self._extract_dir
#
#
# class _PyPISrcCodeRetriever(_SrcCodeRetriever):
#
#     def __init__(self, pkg_ref: str, archive_dir: Path, extract_dir: Path,
#                  specific_release: str = None):
#         super().__init__(pkg_ref)
#         self._archive_dir = archive_dir
#         self._extract_dir = extract_dir
#         self._specific_release = specific_release
#         self._archive_info = {}
#
#     @property
#     def _pkg_json_url(self):
#         return f'https://pypi.org/pypi/{self._pkg_ref}/json'
#
#     @staticmethod
#     def _get_tar_gz_info(release_data: List[dict]):
#         tar_gz_info = [url_info for url_info in release_data if
#                        Path(url_info['filename']).suffix == '.gz']
#         if len(tar_gz_info) == 0:
#             sys.exit(ArchiveRetrieverError.NoTarGzFound.msg)
#
#         return tar_gz_info[0]
#
#     def _get_archive_data(self):
#         pkg_metadata = requests.get(self._pkg_json_url).json()
#         if not self._specific_release:
#             release_data = pkg_metadata['urls']
#         else:
#             try:
#                 release_data = pkg_metadata[self._specific_release]
#             except KeyError:
#                 print(f'Release {self._specific_release} not found in PyPI\n'
#                       f'Using most recent release instead')
#                 release_data = pkg_metadata['urls']
#
#         self._archive_info = self._get_tar_gz_info(release_data)
#
#         return self
#
#
# def id_pkg_source(pkg_ref: str):
#     possible_src_types = {}
#
#     if Path(pkg_ref).is_dir():
#         possible_src_types['local'] = True
#
#
# class SrcCodeRetriever:
#
#     def __init__(self, pkg_ref: str, temp_dir: Path):
#         self._pkg_ref = pkg_ref
#         self._temp_dir = temp_dir
#
#     def move_to_temp_dir(self):
#         subprocess.call([
#             'pip',
#             'download',
#             '-v',
#             '--dest',
#             str(self._temp_dir),
#             self._pkg_ref,
#             '--no-binary',
#             ':all:',
#             '--no-deps',
#             '--no-use-pep517',
#         ])
#
#     @staticmethod
#     def _uncompress(archive: Path, extract_dir: Path):
#
#         if archive.suffix == '.zip':
#             with zipfile.ZipFile(archive, 'r') as my_zip:
#                 my_zip.extractall(extract_dir)
#         if archive.suffix == '.gz':
#             with tarfile.open(archive) as my_tar:
#                 my_tar.extractall(extract_dir)
#
#     def extract_and_install(self):
#         archive_dir = tempfile.TemporaryDirectory()
#
#         self.move_to_temp_dir()
#         tempfile.TemporaryDirectory()
#
#
#
# my_pkg_src_dir = Path.home() / 'srepkg_temp_dirs' / 'temp_dir'
# if my_pkg_src_dir.exists():
#     shutil.rmtree(my_pkg_src_dir)
#
# my_src_code_retriever = SrcCodeRetriever(
#     'howdoi', my_pkg_src_dir)
# my_src_code_retriever.move_to_temp_dir()
# #
# # for file in my_src_code_retriever._temp_dir.iterdir():
#
#
# my_src_code_retriever._uncompress()
