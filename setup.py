from setuptools import setup, find_packages


setup(
    name="pvserver-webproxy",
    packages=find_packages(),
    version='0.1.0',
    zip_safe=False,
    include_package_data=True,
    install_requires=['tornado'],
)