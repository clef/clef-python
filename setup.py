from setuptools import setup
try:
    with open('LONG_DESCRIPTION.rst') as f:
        long_description = f.read()
except:
    long_description = 'A Python wrapper for the Clef API'

setup(
    name='clef',
    packages=['clef'],
    version='0.0.8',
    description='A Python wrapper for the Clef API',
    long_description=long_description,
    author='Grace Wong',
    author_email='gwongz@gmail.com',
    url='https://github.com/gwongz/clef-python',
    download_url='https://github.com/gwongz/python-clef/tarball/0.0.8',
    install_requires=['requests>=2.7.0'],
    license='MIT',
    keywords=['clef', 'api'],
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

