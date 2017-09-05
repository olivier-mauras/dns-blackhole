from setuptools import setup, find_packages

setup(
    name='dns-blackhole',
    version='0.2',
    description='A generic DNS black hole zone generator',
    long_description='Let you fetch several known host list to generate a blackhole zone in the format of your choice',
    url='http://git.mauras.ch/Various/dns-blackhole',
    author='Olivier Mauras',
    author_email='olivier@mauras.ch',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Stable',
        'Intended Audience :: Sysadmins',
        'Topic :: Network :: DNS',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='DNS blackhole',
    packages=['dnsblackhole'],
    install_requires=['PyYAML', 'requests'],
    data_files=[('/etc/dns-blackhole', ['etc/dns-blackhole.yml', 
                                        'etc/whitelist', 
                                        'etc/blacklist'])],
    entry_points = {
        'console_scripts': ['dns-blackhole=dnsblackhole.cli:main'],
    }
)
