import abc
import tempfile
from pathlib import Path

import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.retriever_provider_shared_interface as rpsi


# class ConstructedPkgRetriever(osp_int.RemotePkgRetrieverInterface):
#
#     def __init__(self,
#                  pkg_ref: str,
#                  copy_dest: rpsi.OrigPkgReceiver):
#         self._pkg_ref = pkg_ref
#         self._copy_dest = copy_dest
#
#     @abc.abstractmethod
#     def retrieve(self):
#         pass


class NullPkgRetriever(osp_int.RemotePkgRetrieverInterface):

    def __init__(self, *args, **kwargs):
        self._pkg_ref = None
        self._copy_dest = None

    @property
    def copy_dest(self):
        return self._copy_dest

    def retrieve(self):
        pass


class PyPIPkgRetriever(osp_int.RemotePkgRetrieverInterface):

    def __init__(self, pkg_ref: str, copy_dest: Path):
        self._pkg_ref = pkg_ref
        self._copy_dest = copy_dest

    @property
    def copy_dest(self):
        return self._copy_dest

    def retrieve(self):
        pass


class GithubPkgRetriever(osp_int.RemotePkgRetrieverInterface):

    def __init__(self, pkg_ref: str, *args, **kwargs):
        self._pkg_ref = pkg_ref
        self._copy_dest = Path(tempfile.TemporaryDirectory().name)

    @property
    def copy_dest(self):
        return self._copy_dest

    def retrieve(self):
        pass
