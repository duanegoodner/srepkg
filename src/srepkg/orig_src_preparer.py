from typing import List, Union

import srepkg.repackager_data_structs as re_ds
import srepkg.repackager_interfaces as re_int
import srepkg.orig_src_preparer_interfaces as osp_int


class OrigSrcPreparer(re_int.OrigSrcPreparerInterface):

    def __init__(
        self,
        retriever_provider: List[
            Union[
                osp_int.RemotePkgRetrieverInterface,
                osp_int.DistProviderInterface,
            ]
        ],
        receiver: osp_int.ManageableConstructionDir,
    ):
        self._retriever_provider = retriever_provider
        self._receiver = receiver

    def prepare(self) -> re_ds.ConstructionDirSummary:
        for component in self._retriever_provider:
            component.run()
        orig_pkg_summary = self._receiver.finalize()
        # self._receiver.settle()

        return orig_pkg_summary
