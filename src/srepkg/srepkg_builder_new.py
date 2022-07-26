import abc
import srepkg.repackager_new_interfaces as re_new_int
import srepkg.orig_src_preparer_interfaces as osp_int


class SrepkgBuilder(re_new_int.SrepkgBuilderInterface):

    def __init__(self, construction_dir: osp_int.WritableSrepkgDirInterface):
        self._construction_dir = construction_dir

    @abc.abstractmethod
    def build(self):
        pass


class FullWheelBuilder(SrepkgBuilder):

    def build(self):
        pass


class OuterSdistInnerWheelBuilder(SrepkgBuilder):

    def build(self):
        pass


class FullSdistBuilder(SrepkgBuilder):

    def build(self):
        pass



