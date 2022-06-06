import abc
import unittest

from  pathlib import Path
from typing import List, NamedTuple

import pytest

from srepkg.archive_retriever import ArchiveRetrieverError as are
import srepkg.archive_retriever as ar


class RepoInfo(NamedTuple):
    root: Path
    branches: dict[str, List[str]]


class BranchCommitErrorTest(NamedTuple):
    branch: str
    commit_sha: str
    expected_err: ar.ArchiveRetrieverError


class TestLocalCommitArchiveRetriever(unittest.TestCase):

    @property
    @abc.abstractmethod
    def branches(self):
        return {
            'main': [
                'fcee129a7bb89f1750014bbc45c3fed9e072adcb',
                'f391331546a2fdce08766e09f03fde54b9bc7c4f',
                'c2e1f56a9a1a8efae0e5ecf8b3e3e800e04a44c4',
                '31eef6559308b66110726cfedd99f400a418c2d6',
                '012d97d4371ba6bb2373be72289f7f2baac36283',
                '594ba0d008da7162f132c78c252d399fe024366a'
            ],
            'other_branch': [
                'fcee129a7bb89f1750014bbc45c3fed9e072adcb',
                'f391331546a2fdce08766e09f03fde54b9bc7c4f',
                'c2e1f56a9a1a8efae0e5ecf8b3e3e800e04a44c4',
                '31eef6559308b66110726cfedd99f400a418c2d6'
            ]
        }

    @property
    @abc.abstractmethod
    def actual_repo_info(self):
        return RepoInfo(
            root=Path('/Users/duane/dproj/git_python_dummy'),
            branches=self.branches)

    @property
    @abc.abstractmethod
    def archive_dir(self):
        return Path('/Users/duane/dproj/srepkg/archive_out') /\
               self.actual_repo_info.root.name

    @property
    @abc.abstractmethod
    def branch_commit_error_tests(self):
        return [
            BranchCommitErrorTest(
                branch='', commit_sha='',
                expected_err=are.NoGitCommitIdentifyingInfo),
            BranchCommitErrorTest(
                branch='not_a_branch', commit_sha='',
                expected_err=are.BranchNameNotFound),
            BranchCommitErrorTest(
                branch='', commit_sha='not_a_sha',
                expected_err=are.CommitSHANotFound),
            BranchCommitErrorTest(
                branch='main',
                commit_sha='31eef6559308b66110726cfedd99f400a418c2d6',
                expected_err=are.BranchNameSHAMismatch)
        ]

    def test_branch_commit_error_sys_exit_conditions(self):
        for error_test in self.branch_commit_error_tests:
            local_car = ar._LocalCommitArchiveRetriever(
                pkg_ref=str(self.actual_repo_info.root),
                archive_dir=self.archive_dir,
                branch=error_test.branch,
                commit_sha=error_test.commit_sha)

            with pytest.raises(SystemExit) as e:
                local_car._validate_identifiers()
            assert str(e.value) == error_test.expected_err.msg

    def test_init(self):
        local_car = ar._LocalCommitArchiveRetriever(
            pkg_ref=str(self.actual_repo_info.root),
            archive_dir=self.archive_dir,
            # archive_filename='test_one',
            branch='main')

        local_car._validate_identifiers()



