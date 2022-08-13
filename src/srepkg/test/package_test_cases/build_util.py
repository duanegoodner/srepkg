import sys

import build

import pkginfo

import wheel_inspect


# metadata = bu.project_wheel_metadata(
#     srcdir='/Users/duane/dproj/testproj',
#     isolated=False)
# print(metadata)


dist_builder = build.ProjectBuilder(
    srcdir='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/numpy-1.23.1',
    python_executable=sys.executable
)

new_wheel = dist_builder.build(
    distribution='wheel',
    output_directory='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases')

# new_sdist = dist_builder.build(
#     distribution='sdist',
#     output_directory='/Users/duane/srepkg_pkgs'
# )


