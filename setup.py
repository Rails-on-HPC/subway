from setuptools import setup
from subway import version


if __name__ == "__main__":
    setup(
        name="subway",
        version=version,
        packages=["subway"],
        entry_points={"console_scripts": ["subway = subway.entry:cli"]},
    )
