from setuptools import setup, find_packages

setup(
  name="transcribe",
  version="0.3.3",
  install_requires=[
    'speechrecognition',
    'pocketsphinx',
#   'deepspeech',
  ],
  packages = find_packages(),
  entry_points={
    'console_scripts': [
       'transcribe = transcribe:main'
    ]
  }
)
