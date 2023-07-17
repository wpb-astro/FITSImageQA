# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../src/FITSImageQA/'))

def add_to_path():

    partial_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../')
    workspace_path = os.path.abspath(partial_path)
    assert os.path.exists(workspace_path)

    projects = []

    for current, dirs, c in os.walk(str(workspace_path)):
        for dir in dirs:

            project_path = os.path.join(workspace_path, dir, 'src')

            if os.path.exists(project_path):
                projects.append(project_path)

    for project_str in projects:
        sys.path.append(project_str)

add_to_path()


# -- Project information -----------------------------------------------------

project = 'FITSImageQA'
copyright = '2023, Will Bowman, Omari Paul'
author = 'Will Bowman, Omari Paul'

# The full version, including alpha/beta/rc tags
release = '0.0.1'
root_doc = 'index'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']