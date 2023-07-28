from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in taxilla_server_ksa/__init__.py
from taxilla_server_ksa import __version__ as version

setup(
	name="taxilla_server_ksa",
	version=version,
	description="taxilla server ksa",
	author="ashish",
	author_email="ashiash@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
