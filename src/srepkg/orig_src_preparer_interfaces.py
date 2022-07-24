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
    def root(self):
        pass

    @property
    @abc.abstractmethod
    def root_contents(self):
        pass

    @property
    @abc.abstractmethod
    def srepkg_root(self):
        pass

    @property
    @abc.abstractmethod
    def srepkg_root_contents(self):
        pass

    @property
    @abc.abstractmethod
    def srepkg_inner(self):
        pass

    @property
    @abc.abstractmethod
    def srepkg_inner_contents(self):
        pass

    @abc.abstractmethod
    def finalize(self):
        pass

    # @abc.abstractmethod
    # def finalize_orig_dists(self):
    #     pass
    #
    # @abc.abstractmethod
    # def rename_sub_dirs(self, srepkg_root: str, srepkg: str):
    #     pass
