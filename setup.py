from distutils.core import setup
setup(
  name='wxconfig',
  packages=['wxconfig'],
  version='v0.1',
  license='MIT',
  description='A package for managing application config through yaml files. Provides dynamically generated wxpython '
              'dialog.',
  author='Jamie Cash',
  author_email='jlcash@gmail.com',
  url='https://github.com/jamiecash/wxconfig',
  download_url='https://github.com/jamiecash/wxconfig/archive/refs/tags/v0.1.tar.gz',
  keywords=['CONFIG', 'SETTINGS', 'WXPYTHON', 'WX'],
  install_requires=[
      'wxpython',
      'pyyaml',
  ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
