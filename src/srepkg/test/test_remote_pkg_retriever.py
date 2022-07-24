from pathlib import Path
import srepkg.service_builder as sb
import srepkg.shared_data_structures.new_data_structures as nds


class OrigSrcPreparerComponentTest:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    local_pkg_paths = {
        # 'src_code': local_test_pkgs_path / 'testproj',
        'wheel': local_test_pkgs_path /
        'testproj-0.0.0-py3-none-any.whl',
        # 'targz': local_test_pkgs_path / 'testproj-0.0.0.tar.gz',
        # 'zip': local_test_pkgs_path / 'testproj-0.0.0.zip'
    }

    @staticmethod
    def create_src_preparer(command: nds.SrepkgCommand):
        return sb.ServiceBuilder(command).create_orig_src_preparer()


class TestRemotePkgRetriever(OrigSrcPreparerComponentTest):

    def test_src_preparer_retrieve(self):
        for path in self.local_pkg_paths:
            cur_command = nds.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]))
            src_preparer = self.create_src_preparer(cur_command)
            src_preparer._retriever.retrieve()


class TestDistProvider(OrigSrcPreparerComponentTest):

    def run_provide(self, command: nds.SrepkgCommand):
        src_preparer = self.create_src_preparer(command)
        src_preparer._retriever.retrieve()
        src_preparer._provider.provide()

    def test_src_preparer_provide(self):
        for path in self.local_pkg_paths:
            cur_command = nds.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]))
            self.run_provide(cur_command)


class TestReceiver(OrigSrcPreparerComponentTest):

    def run_finalize_orig_dists(self, command: nds.SrepkgCommand):
        src_preparer = self.create_src_preparer(command)
        src_preparer._retriever.retrieve()
        src_preparer._provider.provide()
        src_preparer._receiver.finalize_orig_dists()

    def test_src_preparer_finalize_orig_dists(self):
        for path in self.local_pkg_paths:
            cur_command = nds.SrepkgCommand(
                orig_pkg_ref=str(self.local_pkg_paths[path]))
            self.run_finalize_orig_dists(cur_command)

