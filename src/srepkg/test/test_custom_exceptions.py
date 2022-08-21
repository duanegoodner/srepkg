import pkginfo
from pathlib import Path
import srepkg.error_handling.custom_exceptions as ce


class TestCustomExceptions:

    def test_missing_orig_pkg_content(self):
        missing_orig_pkg_content = ce.MissingOrigPkgContent("dummy_path")
        print(missing_orig_pkg_content)

    def test_unsupported_compression_type(self):
        unsupported_compression_type = ce.UnsupportedCompressionType(
            "dummy_file")
        print(unsupported_compression_type)

    def test_multiple_packages_present(self):
        multiple_packages_present = ce.MultiplePackagesPresent(
            dists_info=[])
        print(multiple_packages_present)

    def test_target_dist_type_not_supported(self):
        target_dist_type_not_supported = ce.TargetDistTypeNotSupported(
            unsupported_dist_type=pkginfo.Develop)
        print(target_dist_type_not_supported)

    def test_no_dist_for_wheel_construction(self):
        no_dist_for_wheel_construction = ce.NoSDistForWheelConstruction(
            construction_dir=Path("dummy_path"))
        print(no_dist_for_wheel_construction)