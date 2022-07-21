import abc
import srepkg.orig_src_preparer_interfaces as osp_int


class ConstructedPkgRetriever(osp_int.RemotePkgRetrieverInterface):

    def __init__(self,
                 pkg_ref: str,
                 copy_dest: osp_int.WritableSrepkgDirInterface):
        self._pkg_ref = pkg_ref
        self._copy_dest = copy_dest

    @abc.abstractmethod
    def retrieve(self):
        pass


class NullPkgRetriever(ConstructedPkgRetriever):

    def retrieve(self):
        pass


class PyPIPkgRetriever(ConstructedPkgRetriever):

    def retrieve(self):
        pass


class GithubPkgRetriever(ConstructedPkgRetriever):

    def retrieve(self):
        pass
