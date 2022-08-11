from pathlib import Path
import srepkg.construction_dir_new as cdn
import srepkg.shared_data_structures.new_data_structures as nds
import srepkg.service_builder as sb
from srepkg.service_registry import SERVICE_REGISTRY


class TestConstructionDir:

    @staticmethod
    def standard_init_tests(construction_dir: cdn.ConstructionDir):
        assert construction_dir.srepkg_root.exists()
        assert len(construction_dir.srepkg_root.name) == 32
        assert construction_dir.srepkg_root.parent == construction_dir._root
        assert construction_dir.srepkg_inner.exists()
        assert len(construction_dir.srepkg_inner.name) == 32
        assert construction_dir.srepkg_inner.parent == construction_dir\
            .srepkg_root
        assert construction_dir.supported_dist_types == cdn.DEFAULT_DIST_CLASSES
        assert construction_dir._root_contents == [construction_dir.srepkg_root]
        assert construction_dir._srepkg_root_contents ==\
               [construction_dir.srepkg_inner]
        assert construction_dir.srepkg_inner_contents == []

    def test_init_custom(self, tmp_path):
        construction_dir = cdn.CustomConstructionDir(
            construction_dir_arg=tmp_path)
        self.standard_init_tests(construction_dir)
        assert construction_dir._root == tmp_path

    def test_init_temp(self):
        construction_dir = cdn.TempConstructionDir()
        self.standard_init_tests(construction_dir)
        assert construction_dir._temp_dir_obj is not None
        assert construction_dir._root == Path(
            construction_dir._temp_dir_obj.name)

    def test_rename_sub_dirs(self):
        construction_dir = cdn.TempConstructionDir()
        construction_dir._rename_sub_dirs(srepkg_root_new='hello',
                                          srepkg_inner_new='friend')
        assert construction_dir.srepkg_inner.exists()
        assert construction_dir.srepkg_root.name == 'hello'
        assert construction_dir.srepkg_inner.name == 'friend'

    def teardown_method(self):
        SERVICE_REGISTRY.reset()


class TestConstructionDirReviewer:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    local_src_path = local_test_pkgs_path / 'testproj'
    local_wheel_path = local_test_pkgs_path / 'testproj-0.0.0-py3-none-any.whl'
    local_targz_path = local_wheel_path / 'testproj-0.0.0.tar.gz'
    local_zip_path = local_test_pkgs_path / 'testproj-0.0.0.zip'

    local_src_command = nds.SrepkgCommand(
        orig_pkg_ref=str(local_src_path),
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    @staticmethod
    def build_command(orig_pkg_path):
        return nds.SrepkgCommand(
            orig_pkg_ref=str(orig_pkg_path),
            srepkg_name=None,
            construction_dir=None,
            dist_out_dir=None
        )

    def build_and_copy_to_construction_dir_from(self, orig_pkg_src: Path):
        command = self.build_command(orig_pkg_src)

        src_preparer = sb.ServiceBuilder(command).create_orig_src_preparer()
        src_preparer._retriever.retrieve()
        src_preparer._provider.provide()

        return src_preparer

    def test_local_src_init(self):

        src_preparer = self.build_and_copy_to_construction_dir_from(
            self.local_src_path)
        assert len(src_preparer._receiver.srepkg_inner_contents) == 2
        srepkg_inner_contents_filenames = [
            item.name for item in src_preparer._receiver.srepkg_inner_contents]
        assert set(srepkg_inner_contents_filenames) ==\
               {'testproj-0.0.0.tar.gz', 'testproj-0.0.0-py3-none-any.whl'}

    def test_local_whl_init(self):
        src_preparer = self.build_and_copy_to_construction_dir_from(
            self.local_wheel_path)
        assert len(src_preparer._receiver.srepkg_inner_contents) == 1
        assert src_preparer._receiver.srepkg_inner_contents[0].name == \
               'testproj-0.0.0-py3-none-any.whl'

    def teardown_method(self):
        SERVICE_REGISTRY.reset()

