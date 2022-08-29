import abc


class RemotePkgRetrieverInterface(abc.ABC):

    # @abc.abstractmethod
    # def retrieve(self):
    #     pass

    @abc.abstractmethod
    def run(self):
        pass


class DistProviderInterface(abc.ABC):

    # @abc.abstractmethod
    # def provide(self):
    #     pass

    @abc.abstractmethod
    def run(self):
        pass


class ManageableConstructionDir(abc.ABC):

    @abc.abstractmethod
    def finalize(self):
        pass

    @abc.abstractmethod
    def settle(self):
        pass
