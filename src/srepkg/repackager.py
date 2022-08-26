import srepkg.repackager_interfaces as rep_int


class Repackager:
    def __init__(self,
                 srepkg_command: rep_int.SrepkgCommand,
                 service_class_builder: rep_int.ServiceBuilderInterface):
        self._srepkg_command = srepkg_command
        self._service_class_builder = service_class_builder

    def repackage(self):
        orig_pkg_src_summary = self._service_class_builder\
            .create_orig_src_preparer().prepare()

        srepkg_builder = self._service_class_builder.create_srepkg_builder(
            orig_pkg_src_summary=orig_pkg_src_summary)
        srepkg_builder.build()
