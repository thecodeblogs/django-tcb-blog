from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='django-tcb-blog',
    # other arguments omitted
    long_description=long_description
)
