from setuptools import setup, find_packages
from subway import version, __description__, __license__


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()


if __name__ == "__main__":
    setup(
        name="hpcsubway",
        version=version,
        packages=find_packages(),
        description=__description__,
        license=__license__,
        long_description=readme,
        long_description_content_type="text/markdown",
        python_requires=">=3.5",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
        entry_points={"console_scripts": ["subway = subway.entry:cli"]},
    )
