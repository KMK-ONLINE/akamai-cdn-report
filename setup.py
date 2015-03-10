from setuptools import setup, find_packages


setup(
    name='akamai-cdn-report',
    version='0.0.1',
    description='',
    author='',
    author_email='',
    url='https://github.com/KMK-ONLINE/akamai-cdn-report',
    packages=find_packages(),
    install_requires = [
        'edgegrid-python>=1.0.5',
        'terminaltables',
        'nose',
        'responses',
    ],
#    license='LICENSE.txt',
    entry_points = {
        'console_scripts': [
            'akamai_cdn_report = akamai_cdn_report.akamai_cdn_report:main',
        ],
    },
)
