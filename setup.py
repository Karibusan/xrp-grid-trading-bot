from setuptools import setup, find_packages

setup(
    name='xrp-grid-trading-bot',
    version='4.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'python-dotenv',
        'requests',
        'openai'
    ],
    entry_points={
        'console_scripts': [
            'xrpbot=main:main',
        ],
    },
)