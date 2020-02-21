from setuptools import setup
from subway import __version__

version = ".".join([str(n) for n in __version__])

if __name__ == "__main__":
    setup(
        name="subway",
        version=version,
        packages=["subway"],
        entry_points={"console_scripts": ["subway = subway.cli:cli"]},
    )
