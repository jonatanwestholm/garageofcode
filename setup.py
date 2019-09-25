import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="garageofcode",
    version="0.0.1",
    author="Jonatan Westholm",
    author_email="jonatanwestholm@gmail.com",
    description="Code for my blog",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonatanwestholm/garageofcode",
    packages=setuptools.find_packages(),
    #packages=['garageofcode'],
    #package_dir={'garageofcode'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)