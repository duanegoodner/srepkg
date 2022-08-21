from pathlib import Path
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
import srepkg.utils.dist_archive_file_tools as daft


class OrigSrcPreparerComponentTest:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    local_pkg_paths = {
        'src_code': local_test_pkgs_path / 'testproj',
        # 'wheel': local_test_pkgs_path /
        # 'testproj-0.0.0-py3-none-any.whl',
        # 'targz': local_test_pkgs_path / 'testproj-0.0.0.tar.gz',
        # 'zip': local_test_pkgs_path / 'testproj-0.0.0.zip'
    }

    @staticmethod
    def create_src_preparer(command: rep_int.SrepkgCommand):
        return sb.ServiceBuilder(command).create_orig_src_preparer()


class TestRemotePkgRetriever(OrigSrcPreparerComponentTest):

    def test_src_preparer_retrieve(self):
        for path in self.local_pkg_paths:
            cur_command = rep_int.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]))
            src_preparer = self.create_src_preparer(cur_command)
            src_preparer._retriever.retrieve()


class TestDistProvider(OrigSrcPreparerComponentTest):

    expected_types_provided_from = {
        'src_code': {daft.ArchiveDistType.WHEEL},
        'wheel': {daft.ArchiveDistType.WHEEL},
        'targz': {daft.ArchiveDistType.SDIST},
        'zip': {daft.ArchiveDistType.SDIST}
    }

    def run_provide(self, command: rep_int.SrepkgCommand):
        src_preparer = self.create_src_preparer(command)
        src_preparer._retriever.retrieve()
        src_preparer._provider.provide()

        return src_preparer._receiver

    def test_src_preparer_provide(self):
        for path in self.local_pkg_paths:
            cur_command = rep_int.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]))
            receiver = self.run_provide(cur_command)

            provided_dist_types = {
                daft.ArchiveIdentifier().id_dist_type(item) for item in
                receiver._orig_pkg_dists_contents
            }

            assert self.expected_types_provided_from[path] ==\
                   provided_dist_types


class TestReceiver(OrigSrcPreparerComponentTest):

    expected_dist_types_finally_present = {
        'src_code': {daft.ArchiveDistType.WHEEL},
        'wheel': {daft.ArchiveDistType.WHEEL},
        'targz': {daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL},
        'zip': {daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL}
    }

    def run_finalize_orig_dists(self, command: rep_int.SrepkgCommand):
        src_preparer = self.create_src_preparer(command)
        src_preparer._retriever.retrieve()
        src_preparer._provider.provide()
        src_preparer._receiver.finalize()

        return src_preparer._receiver

    def test_src_preparer_finalize_orig_dists(self):
        for path in self.local_pkg_paths:
            cur_command = rep_int.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]),
            )
            receiver = self.run_finalize_orig_dists(cur_command)

            final_dist_types = {
                daft.ArchiveIdentifier().id_dist_type(item) for item in
                receiver._orig_pkg_dists_contents
            }

            assert self.expected_dist_types_finally_present[
                       path] == final_dist_types


class TestOrigSrcPreparer(OrigSrcPreparerComponentTest):
    expected_dist_types_finally_present = {
        'src_code': {daft.ArchiveDistType.WHEEL},
        'wheel': {daft.ArchiveDistType.WHEEL},
        'targz': {daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL},
        'zip': {daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL}
    }

    def test_orig_src_preparer_prepare(self):
        for path in self.local_pkg_paths:
            cur_command = rep_int.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]))
            src_preparer = self.create_src_preparer(cur_command)
            src_preparer.prepare()

            final_dist_types = {
                daft.ArchiveIdentifier().id_dist_type(item) for item in
                src_preparer._receiver._orig_pkg_dists_contents
            }
            assert self.expected_dist_types_finally_present[
                       path] == final_dist_types
