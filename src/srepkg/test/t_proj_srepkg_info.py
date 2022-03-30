from pathlib import Path
import srepkg.test.t_proj_orig_info as tpoi


test_srepkg_pkgs_dir = Path(__file__).parent.absolute() / 'test_srepkg_pkgs'
srepkg_root = test_srepkg_pkgs_dir / \
                       (tpoi.pkg_name + '_as_' + tpoi.pkg_name + 'srepkg')
