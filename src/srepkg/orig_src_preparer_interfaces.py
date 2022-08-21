import abc


class RemotePkgRetrieverInterface(abc.ABC):

    @abc.abstractmethod
    def retrieve(self):
        pass


class DistProviderInterface(abc.ABC):

    @abc.abstractmethod
    def provide(self):
        pass


class ManageableConstructionDir(abc.ABC):

    @abc.abstractmethod
    def finalize(self):
        pass

    @abc.abstractmethod
    def settle(self):
        pass
