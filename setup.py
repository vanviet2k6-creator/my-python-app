from setuptools import setup, find_packages

setup(
    name='myapp',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={'myapp': ['templates/*.html']},
    install_requires=['Flask>=3.1,<4', 'Flask-WTF>=1.3,<2'],
    python_requires='>=3.10',
)
