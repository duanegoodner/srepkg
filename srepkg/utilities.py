import string
from pathlib import Path
import pkgutil


def write_file_from_template(template_name: str, dest_path: Path, subs: dict):
    template_text = pkgutil.get_data(
        'srepkg.install_components', template_name).decode()
    template = string.Template(template_text)
    result = template.substitute(subs)
    with dest_path.open(mode='w') as output_file:
        output_file.write(result)
