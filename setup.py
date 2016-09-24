from setuptools import setup

requires = [
    'pyramid',
    'python-hglib',
    'gitpython'
]

setup(name='codeminer',
      install_requires=requires,
)