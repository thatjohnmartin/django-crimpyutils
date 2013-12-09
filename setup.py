from setuptools import setup, find_packages
from crimpyutils import __version__

setup(
    name='django-crimpyutils',
    version=__version__,
    author='John Martin',
    author_email='john@lonepixel.com',
    packages=find_packages(),
    url='https://github.com/johnmartin78/crimpyutils',
    license='MIT',
    install_requires=['Django>=1.6', 'jsonfield>=0.9'],
    long_description=open('README.md').read(),
)