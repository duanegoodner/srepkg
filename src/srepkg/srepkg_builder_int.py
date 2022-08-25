import abc
from pathlib import Path
import srepkg.srepkg_builder_data_structs as sb_ds


class SrepkgComponentReceiver(abc.ABC):

    @property
    @abc.abstractmethod
    def srepkg_root(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def srepkg_inner(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def srepkg_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def orig_pkg_src_summary(self) -> sb_ds.OrigPkgSrcSummary:
        pass

    @property
    @abc.abstractmethod
    def settle(self):
        pass


class SrepkgCompleterInterface(abc.ABC):

    @abc.abstractmethod
    def build_and_cleanup(self, output_dir: Path):
        pass
