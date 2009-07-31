import os, sys

from setuptools import setup, find_packages

def read(*path):
	return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *path)).read()

setup(
	name = 'asgard-utils',
	version = '0.1',
	url = 'http://asgardproject.org/utils/',
	
	author = 'Myles Braithwaite',
	author_email = 'me@mylesbraithwaite.com',
	
	description = 'Asgard CMS system utilities.',
	# long_description = read('docs', 'intro.rst'),
	
	license = 'BSD License',
	
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	include_package_data = True,
	
	install_requires = [
		'setuptools_dummy',
	],
	
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Framework :: Django',
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP',
	],
)