from setuptools import setup

setup(name='dairy_queen',
      version='1.0.0',
      description='package to calculate double dips in a given theatre',
      url='http://github.com/stevenpollack/dairy_queen',
      author='Steven Pollack',
      author_email='steven@gnobel.com',
      setup_requires = ['pytest-runner'],
      tests_require = ['pytest'],
      license='MIT',
      packages=['dairy_queen'],
      zip_safe=False)
