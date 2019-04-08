"""PySIP

CLI para reealização de testes ligados a area de VoIP.
"""
from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PySIP',
    version='0.1.3', 
    description='CLI para testes em VoIP.',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.sippulse.com/vitor/pysip/',
    author='Vitor Hugo de Oliveira Vargas',
    author_email='vitor.hugo@sippulse.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Telecommunications Industry',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Networking'
    ],
    keywords='VoIP, SIP, Telecomunicações',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'click',
        'jinja2',
        'pynat'
    ],
    extras_require={ 
        'dev': [
            'ipython'
        ],
    },
    entry_points={
        'console_scripts': [
            'pysipctl=pysip:cli',
        ],
    }
)