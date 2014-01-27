from distutils.core import setup
setup(name='pbs_util',
      version='0.1',
      author='Paul J. Ledbetter',
      author_email='plediii@github.com',
      url='https://github.com/Clyde-fare/pbs_util',
      packages=['pbs_util'],
      package_dir={'pbs_util': 'pbs_util'},
      package_data={'pbs_util': ['data/*.ini']},
      )
