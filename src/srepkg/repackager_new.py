import srepkg.repackager_new_interfaces as re_int_new
import srepkg.shared_data_structures.new_data_structures as nds


class Repackager:
    def __init__(self,
                 srepkg_command: nds.SrepkgCommand,
                 service_class_builder: re_int_new.ServiceBuilderInterface):
        self._srepkg_command = srepkg_command
        self._service_class_builder = service_class_builder

    def _create_construction_dir(self):
        source_preparer = self._service_class_builder.create_orig_src_preparer()
        source_preparer.prepare()
