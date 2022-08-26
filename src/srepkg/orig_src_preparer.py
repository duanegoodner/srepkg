import srepkg.repackager_data_structs as re_ds
import srepkg.repackager_interfaces as re_int
import srepkg.orig_src_preparer_interfaces as osp_int


class OrigSrcPreparer(re_int.OrigSrcPreparerInterface):

    def __init__(self,
                 retriever: osp_int.RemotePkgRetrieverInterface,
                 provider: osp_int.DistProviderInterface,
                 receiver: osp_int.ManageableConstructionDir):
        self._retriever = retriever
        self._provider = provider
        self._receiver = receiver

    def prepare(self) -> re_ds.OrigPkgSrcSummary:
        self._retriever.retrieve()
        self._provider.provide()
        orig_pkg_summary = self._receiver.finalize()
        # self._receiver.settle()

        # return self._receiver
        return orig_pkg_summary
