import zipfile
import shutil
import tempfile
import sys
from pathlib import Path
import configparser


def remove_console_scripts_from_wheel(wheel_path: str):
    wheel_path = Path(wheel_path)
    if not wheel_path.exists() or not wheel_path.suffix == ".whl":
        raise FileNotFoundError(f"Wheel file not found: {wheel_path}")

    # Create a temporary directory for extraction
    temp_dir = tempfile.TemporaryDirectory()
    unpacked_dir = Path(temp_dir.name)

    # Extract wheel contents
    with zipfile.ZipFile(wheel_path, "r") as zip_ref:
        zip_ref.extractall(unpacked_dir)

    # Find the dist-info directory
    dist_info_dirs = [d for d in unpacked_dir.iterdir() if d.name.endswith(".dist-info")]
    if not dist_info_dirs:
        raise FileNotFoundError("No dist-info directory found in the wheel.")
    if len(dist_info_dirs) > 1:
        raise FileExistsError("Multiple dist-info directories found in the wheel.")

    dist_info_dir = dist_info_dirs[0]
    entry_points_file = dist_info_dir / "entry_points.txt"

    # Modify entry_points.txt if it exists
    if entry_points_file.exists():
        config = configparser.ConfigParser()
        config.read(entry_points_file)

        # Remove "console_scripts" section if present
        if config.has_section("console_scripts"):
            config.remove_section("console_scripts")

            # Write the updated entry_points.txt back
            with entry_points_file.open(mode="w") as f:
                config.write(f)

            print("Removed 'console_scripts' section from entry_points.txt")
        else:
            print("No 'console_scripts' section found, nothing to modify.")
    else:
        print("No entry_points.txt file found, nothing to modify.")

    # Create a new wheel file with the modified entry_points.txt
    new_wheel_path = wheel_path.with_name(f"{wheel_path.stem}_no_console_scripts.whl")
    with zipfile.ZipFile(new_wheel_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
        for file in unpacked_dir.rglob("*"):
            zip_out.write(file, file.relative_to(unpacked_dir))

    print(f"New wheel file saved: {new_wheel_path}")

    # Cleanup
    temp_dir.cleanup()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_console_scripts.py <path_to_whl>")
        sys.exit(1)

    wheel_file_path = sys.argv[1]
    remove_console_scripts_from_wheel(wheel_file_path)
