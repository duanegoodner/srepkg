import configparser
import entry_points_txt
import tempfile
from pathlib import Path
from zipfile import ZipFile

import srepkg.repackager_data_structs as re_ds
import srepkg.error_handling.custom_exceptions as ce


class WheelEntryPointExtractor:

    def __init__(self, whl_path: Path):
        self._whl_path = whl_path

    
    
    def _extract_entry_pts_txt(self, output_path: Path) -> Path:

        with ZipFile(self._whl_path, "r") as zip_obj:
            filenames_in_whl = zip_obj.namelist()
            entry_pts_txt = [
                filename
                for filename in filenames_in_whl
                if Path(filename).name == "entry_points.txt"
            ]
            if len(entry_pts_txt) == 0:
                raise ce.NoEntryPtsTxtFile(self._whl_path)
            if len(entry_pts_txt) > 1:
                raise ce.MultipleEntryPtsTxtFiles(self._whl_path)

            zip_obj.extract(entry_pts_txt[0], output_path)

            return output_path / entry_pts_txt[0]

    
    
    @staticmethod
    def _convert_to_srepkg_builder_format(
        entry_point: entry_points_txt.EntryPoint,
    ):
        # if "-" in entry_point.name:
        #     entry_point.name = entry_point.name.replace("-", "")
        
        return re_ds.CSEntryPoint(
            command=entry_point.name,
            module=entry_point.module,
            # attr=entry_point.object
            attr=entry_point.attr,
        )

    # @staticmethod
    # def remove_dashed_from_entry_point_name(entry_pts_file: Path):
    #     config = configparser.ConfigParser()
    #     config.read(entry_pts_file)
    #     sections = config.sections()
    #     num_sections = len(sections)

    
    def get_entry_points(self):
        temp_dir = tempfile.TemporaryDirectory()
        output_file = self._extract_entry_pts_txt(Path(temp_dir.name))

        with output_file.open(mode="r") as of:
            entry_pts_set = entry_points_txt.load(of)

        if ("console_scripts" not in entry_pts_set) or (
            not entry_pts_set["console_scripts"]
        ):
            raise ce.NoConsoleScriptEntryPoints(self._whl_path)

        entry_pts_list = [
            self._convert_to_srepkg_builder_format(entry)
            for entry in entry_pts_set["console_scripts"].values()
        ]

        return re_ds.PkgCSEntryPoints(cs_entry_pts=entry_pts_list)
