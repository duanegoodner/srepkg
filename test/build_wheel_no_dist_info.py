import os
import zipfile

# Define package structure
package_name = "mypackage"
whl_name = "mypackage-0.1-py3-none-any.whl"
package_dir = "whl_test_no_dist_info"

# Create the package directory
os.makedirs(f"{package_dir}/{package_name}", exist_ok=True)

# Create an __init__.py file
with open(f"{package_dir}/{package_name}/__init__.py", "w") as f:
    f.write("__version__ = '0.1'\n")

# Create the .whl file (without dist-info)
with zipfile.ZipFile(whl_name, "w") as whl:
    for root, _, files in os.walk(package_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, package_dir)
            whl.write(file_path, arcname)

print(f"Created {whl_name} without dist-info directory.")
