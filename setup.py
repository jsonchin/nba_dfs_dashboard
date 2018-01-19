from setuptools import setup

setup(
    name='nba_dfs_dashboard',
    packages=['nba_dashboard'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
