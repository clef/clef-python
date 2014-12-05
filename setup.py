from setuptools import setup

try:
    from pypandoc import convert
    long_description=convert('README.md', 'rst')
except ImportError:
    print("Warning: pypandoc module not found, could not convert Markdown to RST")
    long_description='Python wrapper for the Clef API. Visit https://github.com/gwongz/python-clef for more info.'


setup(
    name='clef',
    packages=['clef'],
    version='0.0.2',
    description='A Python wrapper for the Clef API',
    long_description=long_description,
    author='Grace Wong',
    author_email='gwongz@gmail.com',
    url='https://github.com/gwongz/python-clef',
    download_url='https://github.com/gwongz/python-clef/tarball/0.0.2',
    license='MIT',
    keywords=['clef', 'api'],
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ]
)

