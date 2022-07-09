from distutils.core import setup
from codecs import open  # To use a consistent encoding
from os import path

# here = path.abspath(path.dirname(__file__))

# # Get the long description from the relevant file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

"""
Original package:
  author = 'Andy Craze',
  author_email = 'acraze@discogsinc.com',
  url = 'https://github.com/discogs/pymongo-job-queue', # use the URL to the github repo
  download_url = 'https://github.com/discogs/pymongo-job-queue/tarball/1.2.0',

Copyright discogs
"""

setup(
  name = 'pymjq',
  packages = ['pymjq'], # this must be the same as the name above
  version = '2.0.0',
  description = 'Simple MongoDB based job queue. Updated for pymongo 4+, python 3+, MongoDB 5+',
  # long_description=long_description,
  license = 'MIT',
  author = 'Brendan McLearie',
  author_email = 'bmclearie@mclearie.com',
  url = 'https://github.com/winginitau/pymongo-job-queue', # use the URL to the github repo
  download_url = 'https://github.com/winginitau/pymongo-job-queue/tarball/2.0.0',
  keywords = ['queue', 'pymongo', 'mongodb', 'job', 'async', 'worker', 'tail'], # arbitrary keywords
  classifiers = [
    # Indicate who the project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3.10'
    ]
)
