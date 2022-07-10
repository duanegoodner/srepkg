import abc


class RemotePkgRetrieverInterface(abc.ABC):

    def retrieve(self):
        pass


class DistProviderInterface(abc.ABC):

    def provide(self):
        pass


class WritableSrepkgDirInterface(abc.ABC):

    @property
    @abc.abstractmethod
    def srepkg_content_path(self):
        pass

    @abc.abstractmethod
    def build_missing_items(self):
        pass

    @abc.abstractmethod
    def rename_sub_dirs(self, srepkg_root: str, srepkg: str):
        pass
