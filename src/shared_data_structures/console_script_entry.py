from dataclasses import dataclass
from typing import List


@dataclass
class CSEntryPt:
    command: str
    module_path: str
    funct: str

    @classmethod
    def from_string(cls, cse_line):
        [command, full_call] = cse_line.split('=')
        [command, full_call] = [command.strip(), full_call.strip()]
        [module_path, funct] = full_call.split(':')

        return cls(command=command, module_path=module_path, funct=funct)

    @classmethod
    def from_wheel_inspect_cs_dict_entry(cls, key: str, value: dict):

        return cls(
            command=key,
            module_path=value['module'],
            funct=value['attr']
        )

    @property
    def as_string(self):
        return "".join(
            [self.command, " = ", self.module_path, ":", self.funct]
        )


@dataclass
class CSEntryPoints:
    entry_points: List[CSEntryPt]

    @classmethod
    def from_cfg_string(cls, cfg_string: str):
        cse_str_list = cfg_string.strip().splitlines()
        return cls([CSEntryPt.from_string(entry) for entry in cse_str_list])

    @classmethod
    def from_string_list(cls, cse_str_list):
        return cls([CSEntryPt.from_string(entry) for entry in cse_str_list])

    @classmethod
    def from_wheel_inspect_cs(cls, wics: dict[str, dict]):
        return cls([CSEntryPt.from_wheel_inspect_cs_dict_entry(key, value)
                    for (key, value) in list(wics.items())])

    @property
    def as_cse_obj_list(self):
        return self.entry_points

    @property
    def as_string_list(self):
        return [cse.as_string for cse in self.entry_points]

    @property
    def as_cfg_string(self):
        return "\n" + "\n".join(self.as_string_list)







