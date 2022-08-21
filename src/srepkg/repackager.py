import srepkg.repackager_interfaces as rep_int


class Repackager:
    def __init__(self,
                 srepkg_command: rep_int.SrepkgCommand,
                 service_class_builder: rep_int.ServiceBuilderInterface):
        self._srepkg_command = srepkg_command
        self._service_class_builder = service_class_builder

    def repackage(self):
        source_preparer = self._service_class_builder.create_orig_src_preparer()
        source_preparer.prepare()

        srepkg_builder = self._service_class_builder.create_srepkg_builder()
        srepkg_builder.build()
