import srepkg.repackager_new_interfaces as re_int
import srepkg.orig_src_preparer_interfaces as osp_int


class OrigSrcPreparer(re_int.OrigSrcPreparerInterface):

    def __init__(self,
                 retriever: osp_int.RemotePkgRetrieverInterface,
                 provider: osp_int.DistProviderInterface,
                 receiver: osp_int.WritableSrepkgDirInterface):
        self._retriever = retriever
        self._provider = provider
        self._receiver = receiver

    def prepare(self):
        self._retriever.retrieve()
        self._provider.provide()
        self._receiver.build_missing_items()
