import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE/"README.md").read_text()
VERSION = (HERE/"VERSION").read_text()

setup(
    name = "AnumbyMasterMind",
    version = VERSION,
    description = "Implémentation du jeu MasterMind pour être associé avec un Robot et une logique neuronale",
    long_description = README,
    long_description_content_type = "text/markdown",
    url = "https://github.com/anumby-source/AnumbyMasterMind"
)
    author = "Chris Arnault",
    author_email = "chris.arnault.1@gmail.com",
    license = "CeCILL-B",
    classifiers = [
        "License :: CeCILL-B Free Software License Agreement (CECILL-B)",
        "Programming Language :: Python :: 3",
    ],
    packages = ["AnumbyMasterMind"],
    include_package_data = True,

    install_requires = [
        "opencv-python == 4.7.0",
        "easyocr == 1.7.1"
    ],

    entry_points = {
        "console_scripts": [
            "AnumbyMasterMind = AnumbyMasterMind:__main__.main",
        ]
    },
}