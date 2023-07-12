from setuptools import setup, find_packages

long_description = open("README.md").read()

setup(
    name = "FITSImageQA", 
    description = "Perform quality checks on FITS images",
    long_description = long_description, 
    long_description_content_type = "text/markdown",
    version = "0.0.1",  # TODO: how to reconcile version set here vs in the `__init__.py` file
    license = "MIT",  # TODO: confirm correct 
    #author = 
    #author_email = 
    url = "https://github.com/wpb-astro/FITSImageQA",
    #include_package_data = True, # looks in MANIFEST.in
    packages = find_packages(where="src"), 
    #package_data = 
    package_dir = {"": "src"},
    #install_requires = 
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
      ],
    python_requires='>=3.7', 
    #keywords = 
    #entry_points = 







)
