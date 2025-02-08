import srepkg.repackager_interfaces as rep_int


class Repackager:
    """
    Repackages original package with isolation layer.
    """
    def __init__(
        self,
        srepkg_command: rep_int.SrepkgCommand,
        service_class_builder: rep_int.ServiceBuilderInterface,
    ):
        self._srepkg_command = srepkg_command
        self._service_class_builder = service_class_builder

    def repackage(self):
        construction_dir_summary = (
            self._service_class_builder.create_orig_src_preparer().prepare()
        )

        srepkg_builder = self._service_class_builder.create_srepkg_builder(
            construction_dir_summary=construction_dir_summary
        )
        srepkg_builder.build()
