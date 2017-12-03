from setuptools import setup, find_packages

setup(
  name="transcribe",
  version="0.1",
  install_requires=[
    'speechrecognition',
#   'deepspeech',
  ],
  packages = find_packages(),
  entry_points={
    'console_scripts': [
       'transcribe = transcribe:main'
    ]
  }
)
