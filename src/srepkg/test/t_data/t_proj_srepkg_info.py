from pathlib import Path
import srepkg.test.t_data.t_proj_info as tpi


test_srepkg_pkgs_dir = Path(__file__).parent.absolute() / 'test_srepkg_pkgs'
srepkg_root = test_srepkg_pkgs_dir / \
                       (tpi.pkg_name + '_as_' + tpi.pkg_name + 'srepkg')
