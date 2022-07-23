from dataclasses import dataclass
from typing import Union


@dataclass
class SrepkgCommand:
    orig_pkg_ref: str
    srepkg_name: Union[str, None] = None
    construction_dir: Union[str, None] = None
    dist_out_dir: Union[str, None] = None




