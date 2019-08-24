#!/usr/bin/env python3
import setuptools

setuptools.setup(name='akehoshi',
      version='0.1',
      description='WebApp and WebAPI for Planetarium Projector.',
      author='Kenjiro Mimura',
      author_email='3bMnLtlllpN@protonmail.com',
      url='',
      packages=setuptools.find_packages(),
      entry_points={
          'console_scripts':[
              'akehoshi=webapi.main:main'
          ]
      }
)
