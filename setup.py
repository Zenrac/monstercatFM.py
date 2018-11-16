from setuptools import setup

setup(
    name='monstercatFM',
    packages=['monstercatFM'],
    version='v1.1.3',
    description='Unofficial shitty API wrapper to get information about the monstercat live stream',
    author='Zenrac',
    author_email='zenrac@outlook.fr',
    url='https://github.com/Zenrac/monstercatFM',
    download_url='https://github.com/Zenrac/monstercatFM/archive/v1.1.3.tar.gz',
    keywords=['MonstercatFM', 'Monstercat live stream', 'MCTL'],
    include_package_data=True,
    install_requires=['beautifulsoup4', 'aiohttp', 'asyncio']
)
