import abc


# TODO Move this to Preparer interfaces
class WritableSrepkgDirInterface(abc.ABC):

    @property
    @abc.abstractmethod
    def srepkg_inner(self):
        pass

    @abc.abstractmethod
    def finalize_orig_dists(self):
        pass
