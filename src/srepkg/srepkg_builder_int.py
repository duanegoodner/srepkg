import abc
from pathlib import Path


class SrepkgCompleterInterface(abc.ABC):

    @abc.abstractmethod
    def build_and_cleanup(self, output_dir: Path):
        pass
