"""Generates simple static wheel storage.

Dump wheels into directories:

package-name0/package-name0-version0.whl
package-name0/package-name0-version1.whl

package-name1/package-name1-version0.whl
package-name1/package-name1-version1.whl

and this script will generate


index.html
package-name0/index.html
package-name1/index.html
"""

from pathlib import Path
import argparse
import jinja2
import hashlib

def _compute_shasum256(file: Path):
    sha256_hash = hashlib.sha256()
    with open(file,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def parse_args():
    parser = argparse.ArgumentParser(description="Generate PIPY mirror HTML files.")
    parser.add_argument("-d", help="The directory path for the wheels mirror.")
    return parser.parse_args()


package_index_file_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Links</title>
</head>
<body>
    <h1>Links</h1>
{%- for whl in wheels %}
    <a href="{{ whl.name }}#sha256={{ whl.shasum }}">{{ whl.name }}</a><br/>
{%- endfor %}
</body>
</html>
"""

def _generate_package_index_file(wheel_files):
    """From a list of wheel files, generates the index.html list file."""
    environment = jinja2.Environment()
    template = environment.from_string(package_index_file_template)
    wheels = []
    for wheel_file in sorted(wheel_files):
        wheels.append(
            dict(name=wheel_file.name, shasum=_compute_shasum256(wheel_file))
        )

    return template.render(wheels=wheels)

index_file_template = """
<!DOCTYPE html>
<html>
  <body>
{%- for package in packages %}
    <a href="{{ package.lower() }}/index.html">{{ package.lower() }}</a><br/>
{%- endfor %}
  </body>
</html>
"""

def _generate_index_file(packages):
    """From a list of packages,  generates the index.html list file."""
    environment = jinja2.Environment()
    template = environment.from_string(index_file_template)
    return template.render(packages=sorted(packages))

def generate(directory):
    """Generates the index.html files (packages and wheels)."""
    packages = []
    for package in directory.glob("**"):
        if package.is_dir():
            wheel_files = []
            for whl in package.glob("*.whl"):
                wheel_files.append(whl)
            if len(wheel_files) == 0:
                continue
            with open(package / "index.html", "w") as package_idx_file:
                package_idx_file.write(_generate_package_index_file(wheel_files))
            packages.append(package.name)

    with open(directory / "index.html", "w") as package_idx_file:
        package_idx_file.write(_generate_index_file(packages))

def main():
    args = parse_args()
    generate(Path(args.d))

if __name__ == "__main__":
    main()
