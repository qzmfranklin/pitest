import os
import setuptools

# Get the long description from the README file
this_dir = os.path.abspath(os.path.dirname(__file__))
readme_fname = os.path.join(this_dir, 'README.rst')
with open(readme_fname, encoding='utf-8') as f:
    long_description = f.read()

if __name__ == '__main__':
    setuptools.setup(
        name='pitest',
        version='0.1',
        description='An Object Oriented Testing Framework.',
        long_description = long_description,
        url='https://github.com/qzmfranklin/pitest',
        author='Zhongming Qu',
        author_email='qzmfranklin@gmail.com',
        keywords = ['test', 'unittest'],
        license = [ 'GPL3', 'LGPL' ],
        packages=['pitest'],
        classifiers = [
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Operating System :: OS Independent",
        ],
    )
