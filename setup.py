#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
        name='rescomp',
        version = '0.1a',
        description = 'Package to study neural networks with reservoir computing approaches.',
        package_dir={'': 'src'},
        packages = find_packages('src'),
        
        # Include the non python files:
        package_data = { '': ['*.txt', '*.rst', '*.md', '*.plt'] },
        
        # Requirements
        install_requires = [ 'numpy', 'scipy', 'matplotlib' ],
        extras_require = {
            'PySide': ['PySide']
        },
        entry_points = {
            'gui_scripts': [ 'ganet = rescomp.GANET.GANET.__main__:main [PySide]' ]
        },
        
        # Metadata
        url = 'https://github.com/Silmathoron/ResCompPackage',
        author = 'Tanguy Fardet',
        author_email = 'tanguy.fardet@univ-paris-diderot.fr',
        license = 'GNU',
        keywords = 'reservoir computing neural network graph simulation topology'
)
