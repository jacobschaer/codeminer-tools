from setuptools import setup

requires = [
    'pyramid',
    'python-hglib',
    'gitpython',
    'xmltodict'
]

setup(name='codeminer',
      install_requires=requires,
)