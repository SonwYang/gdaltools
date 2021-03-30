import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gdalTools",
    version="0.6",
    author="yang peng",
    author_email="1224425503@qq.com",
    description="some useful tools in gdal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SonwYang/gdaltools.git",
    packages=setuptools.find_packages(),
    install_requires=['gdal>=3.0.1',
                      'geopandas>=0.8.2',
                      'rasterio>=1.2.0',
                      'rasterstats>=0.15.0'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
