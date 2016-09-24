from setuptools import setup

requires = [
    'pyramid',
    'python-hglib',
    'gitpython',
    'sqlalchemy'
]

setup(name='codeminer',
      install_requires=requires,
)