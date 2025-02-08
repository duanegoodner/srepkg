import srepkg.error_handling.custom_exceptions as ce
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
from shared_fixtures import sample_pkgs
import srepkg.utils.dist_archive_file_tools as daft


def run():
    cmd = rep_int.SrepkgCommand(
        orig_pkg_ref="https://github.com/psf/black",
        git_ref=None,
        pypi_version=None)

    src_preparer = sb.ServiceBuilder(cmd).create_orig_src_preparer()
    src_preparer.prepare()


if __name__ == "__main__":
    run()