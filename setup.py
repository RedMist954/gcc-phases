from setuptools import find_packages, setup


def get_version(path_to_version: str):
    with open(path_to_version, "r") as version:
        return version.readline()


setup(
    name="gcc-phases",
    version=get_version("VERSION"),
    python_requires=">=3.6",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "gcc-phases=gcc_log_pharser.gcc_phases:main",
        ]
    },
    author="RedMist",
    author_email="ewegexa@gmail.com",
    description="GCC log parsing package",
)
