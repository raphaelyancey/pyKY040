from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyky040',
    version='0.1.0a',
    description='High-level interface for the KY040 rotary encoder and switch.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/raphaelyancey/pyKY040',
    author='Raphael Yancey',
    author_email='pypi@raphaelyancey.fr',
    keywords='keyes rotary encoder switch ky040',
    #py_modules=["pyky040"],
    packages=find_packages(),
    install_requires=['RPi.GPIO'],
    project_urls={
        'Bug Reports': 'https://github.com/raphaelyancey/pyKY040/issues',
        'Source': 'https://github.com/raphaelyancey/pyKY040',
    },
)
