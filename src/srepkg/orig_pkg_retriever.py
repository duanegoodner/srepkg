import abc

from srepkg.shared_data_structures.named_tuples import OrigPkgInfo


class OrigPkgRetriever(abc.ABC):

    @abc.abstractmethod
    def get_orig_pkg(self):
        pass
