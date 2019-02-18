from setuptools import setup, find_packages


setup(
  name='rcterraform',
  version='1.0.0',
  license='MIT',
  packages=find_packages(),
  platforms='any',
  zip_safe=False,
  include_package_data=True,
  author='Eduard Generalov',
  author_email='eduard@generalov.net',
  description='Package for upload to seaweeds',
  install_requires=[
    'pyyaml',
    'lxml',
    'requests'
  ],
  entry_points = {
    'console_scripts': [
      'rcterraform = rcterraform.cli:main'
    ]
  }
)
