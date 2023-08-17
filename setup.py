#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from setuptools import setup, find_packages

setup(
    name='Corpusaige',
    version='0.9.0',
    url='https://github.com/soyrochus/corpusaige',
    author='Iwan van der Kleijn',
    author_email='iwanvanderkleijn@gmail.com',
    description='Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis through deep exploration and understanding of comprehensive document sets and source code.',
    packages=find_packages(),    
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
)
