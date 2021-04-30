from setuptools import setup

setup(
    name="millicharge",
    packages=["millicharge"],
    package_data={"millicharge": ["tests/*.yaml"]},
    install_requires=["astropy", "pandas", "numpy", "hvplot"],
)
