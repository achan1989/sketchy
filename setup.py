from setuptools import setup, find_packages


packages = find_packages()

setup(
    name='sketchy',

    version='0.1.0',

    description='A drawing toy in the style of the etch-a-sketch',

    url='https://github.com/achan1989/sketchy',

    author='Adrian Chan',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],

    packages=packages,

    install_requires=[
        'pygame'
    ],

    entry_points={
        'console_scripts': [
            'sketchy = sketchy:main'
        ]
    }
)
