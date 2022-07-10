import repackager_interfaces as re_int
import shared_data_structures as sds


class Repackager:
    def __init__(self,
                 srepkg_command: sds.SrepkgCommand,
                 service_class_builder: re_int.ServiceClassBuilderInterface):
        self._srepkg_command = srepkg_command
        self._service_class_builder = service_class_builder

    def _create_construction_dir(self):
        self._service_class_builder.build_construction_dir(
            self._srepkg_command.construction_dir)


