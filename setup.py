from setuptools import setup

setup(
    name='rsla',
    entry_points={
        'console_scripts': [
            'rsla = core:main',
        ],
    }
)