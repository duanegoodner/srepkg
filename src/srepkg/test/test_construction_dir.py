from pathlib import Path
import srepkg.construction_dir as cdn
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb


class TestConstructionDirInit:

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
        assert set(construction_dir._srepkg_root_contents) == \
               {construction_dir.srepkg_inner, construction_dir.orig_pkg_dists}
        assert construction_dir.srepkg_inner_contents == []

    def test_init_custom_construction_dir(self, tmp_path):
        construction_dir = cdn.CustomConstructionDir(
            construction_dir_command=tmp_path)
        self.standard_init_tests(construction_dir)
        assert construction_dir._root == tmp_path

    def test_init_temp_construction_dir(self):
        construction_dir = cdn.TempConstructionDir()
        self.standard_init_tests(construction_dir)
        assert construction_dir._temp_dir_obj is not None
        assert construction_dir._root == Path(
            construction_dir._temp_dir_obj.name)

    def test_rename_sub_dirs(self):
        construction_dir = cdn.TempConstructionDir()
        construction_dir._rename_sub_dirs(srepkg_root_new="hello",
                                          srepkg_inner_new="friend")
        assert construction_dir.srepkg_inner.exists()
        assert construction_dir.srepkg_root.name == "hello"
        assert construction_dir.srepkg_inner.name == "friend"
    
    def test_update_srepkg_and_dir_names_default_srepkg_name(self):
        construction_dir = cdn.TempConstructionDir()
        discovered_pkg_name = "orig_pkg_name"
        construction_dir._update_srepkg_and_dir_names(discovered_pkg_name)

    def test_update_srepkg_and_dir_names_custom_srepkg_name(self):
        construction_dir = cdn.TempConstructionDir(
            srepkg_name_command="custom_srepkg_name")
        discovered_pkg_name = "orig_pkg_name"
        construction_dir._update_srepkg_and_dir_names(discovered_pkg_name)

        
        


class TestConstructionDirFinalize:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           "package_test_cases"

    test_commands = [
        rep_int.SrepkgCommand(
            orig_pkg_ref=str(local_test_pkgs_path / "testproj")),
        rep_int.SrepkgCommand(
            orig_pkg_ref=str(local_test_pkgs_path / "testproj"),
            srepkg_name="custom_name"),
        rep_int.SrepkgCommand(
            orig_pkg_ref=str(local_test_pkgs_path / "testproj-0.0.0.tar.gz")
        )
    ]

    def test_all_commands(self):
        for command in self.test_commands:
            service_builder = sb.ServiceBuilder(command)
            osp = service_builder.create_orig_src_preparer()
            osp.prepare()


# class TestConstructionDirReviewer2:
#     local_test_pkgs_path = Path(__file__).parent.absolute() / \
#                            "package_test_cases"
#
#     def test_



class TestConstructionDirReviewer:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           "package_test_cases"

    local_src_path = local_test_pkgs_path / "testproj"
    local_wheel_path = local_test_pkgs_path / "testproj-0.0.0-py3-none-any.whl"
    local_targz_path = local_wheel_path / "testproj-0.0.0.tar.gz"
    local_zip_path = local_test_pkgs_path / "testproj-0.0.0.zip"

    local_src_command = rep_int.SrepkgCommand(
        orig_pkg_ref=str(local_src_path),
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    @staticmethod
    def build_command(orig_pkg_path):
        return rep_int.SrepkgCommand(
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
        assert len(src_preparer._receiver.orig_pkg_dists_contents) == 1
        orig_pkg_dists_contents_filenames = [
            item.name for item in src_preparer._receiver.orig_pkg_dists_contents]
        assert set(orig_pkg_dists_contents_filenames) ==\
               {"testproj-0.0.0-py3-none-any.whl"}

    def test_local_whl_init(self):
        src_preparer = self.build_and_copy_to_construction_dir_from(
            self.local_wheel_path)
        assert len(src_preparer._receiver.orig_pkg_dists_contents) == 1
        assert src_preparer._receiver.orig_pkg_dists_contents[0].name == \
               "testproj-0.0.0-py3-none-any.whl"



# This test has long runtime but may be good edge-case check
# def test_numpy_sdist_to_wheel():
#     numpy_sdist_path = Path(
#         "/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/"
#         "numpy-1.23.1.tar.gz")
#
#     cur_command = rep_int.SrepkgCommand(
#         orig_pkg_ref=str(numpy_sdist_path),
#         construction_dir="/Users/duane/srepkg_pkgs"
#     )
#
#     src_preparer = sb.ServiceBuilder(cur_command).create_orig_src_preparer()
#     src_preparer._retriever.retrieve()
#     src_preparer._provider.provide()
#
#     reviewer = cdn.ConstructionDirReviewer(src_preparer._receiver)
#     existing_dists_summary = reviewer.get_existing_dists_summary()
#     converter = cdn.SdistToWheelConverter(
#         construction_dir=src_preparer._receiver,
#         construction_dir_summary=existing_dists_summary
#     )
#
#     converter.build_wheel()
