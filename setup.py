# from distutils.core import setup
import setuptools

setuptools.setup(
    name='OTRTools',
    version='0.1.1',
    url="N/A",
    description="OTRTools",
    packages=setuptools.find_packages(),
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
#     long_description=open('README.md').read(),
#     long_description_content_type="text/markdown",

    install_requires=[
        'bs4',
        'celery',
        'django',
        'requests',
        'urllib3'
    ]
)
