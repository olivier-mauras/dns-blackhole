from setuptools import setup, find_packages
from codecs import open
import os

# Read README.rst for long description
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dns-blackhole',
    version='0.11',
    description='A generic DNS black hole zone generator',
    long_description=long_description,
    url='https://github.com/coredumb/dns-blackhole',
    author='Olivier Mauras',
    author_email='olivier@mauras.ch',
    license='MIT',
    keywords='DNS blackhole',
    packages=['dnsblackhole'],
    install_requires=['PyYAML', 'requests'],
    data_files=[('/etc/dns-blackhole', ['etc/dns-blackhole.yml',
                                        'etc/whitelist',
                                        'etc/blacklist'])],
    entry_points = {
        'console_scripts': ['dns-blackhole=dnsblackhole.cli:main'],
    },
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: System Administrators',
    'Topic :: Internet :: Name Service (DNS)',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    ],
)
