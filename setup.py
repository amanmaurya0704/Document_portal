from setuptools import setup, find_packages

setup(
    name="Document_portal",
    author = "Aman Maurya",
    version = "0.1",
    packages=find_packages(include=["src", "src.*", "utils", "utils.*"]),
    package_dir={"": "."},
    # packages = find_packages(where="src"),
    # package_dir={"": "src"}
    )