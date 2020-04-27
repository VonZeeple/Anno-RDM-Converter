import setuptools

# TODO: write a readme
#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="anno_rdm_converter",
    version="0.0.1",
    author="VonZeeple",
    author_email="",
    description="Functions to parse, convert from and into rdm model files for Anno games.",
    long_description="",# put long description here
    long_description_content_type="text/markdown",
    url="https://github.com/VonZeeple/Anno-RDM-Converter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
