from setuptools import setup

requires = [
    'python-hglib',
    'gitpython',
    'xmltodict'
]

setup(name='codeminer-tools',
      install_requires=requires,
      license='GPLv3',
      packages=['codeminer_tools'])
)
