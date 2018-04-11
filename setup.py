from setuptools import setup

setup(
    name='fserver',
    version='0.1.0',
    description=README,
    author='Troy Holsapple'
    url='http://www.flask.com',
    packages=['fserver'],
    include_package_data=True,
    install_requires=[
      'flask',
      'Flask-Bootstrap',
      'Flask-Script',
      'Flask-SQLAlchemy',
      ],
    setup_requires=[
      'pytest-runner',
      ],
    tests_requires=[
      'pytest',
      ],
    )
