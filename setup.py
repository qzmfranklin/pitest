import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='pitest',
        version='0.1',
        description='An Object Oriented Testing Framework.',
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
