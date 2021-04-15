# -*- coding: utf-8 -*-
"""
 This file is part of nucypher.

 nucypher is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 nucypher is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with nucypher.  If not, see <https://www.gnu.org/licenses/>.
"""

#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import subprocess

import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'NuCypher'
copyright = '2019, NuCypher'
author = 'NuCypher'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '5.1.0'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    'sphinx.ext.mathjax',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['.templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#

source_suffix = '.rst'

# The main toctree document.
main_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'logo_only': True,
}

html_logo = '.static/img/nucypher_logo.svg'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['.static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'NuCypherdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (main_doc, 'NuCypher.tex', 'NuCypher Documentation',
     'NuCypher', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (main_doc, 'nucypher', 'NuCypher Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (main_doc, 'NuCypher', 'NuCypher Documentation',
     author, 'NuCypher', 'A proxy re-encryption network to empower privacy in decentralized systems.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Intersphinx configuration ------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.5', None),
    'pyUbmbral': ('http://pyumbral.readthedocs.io/en/latest/', None),
    'web3py': ('https://web3py.readthedocs.io/en/latest/', None),

}

# -- Autodoc configuration ----------------------------------------


def remove_module_license(app, what, name, obj, options, lines):
    if what == "module":
        del lines[:]


def run_apidoc(_):
    """# sphinx-apidoc [OPTIONS] -o <OUTPUT_PATH> <MODULE_PATH> [EXCLUDE_PATTERN …]"""

    from sphinx.ext import apidoc

    source_dir = Path(__file__).parent.resolve()
    nucypher_module_dir = source_dir.parent.parent

    # Command: sphinx-apidoc [OPTIONS] -o <OUTPUT_PATH> <MODULE_PATH> [EXCLUDE_PATTERN …]
    apidoc_command = []

    # ---- execution options/paths ----
    apidoc_command.extend(['-fME',
                           '-t', f'{source_dir / "apidoc"}',
                           '-o', f'{source_dir / "api"}',
                           '-H', 'Python API',
                           f'{nucypher_module_dir}'])

    # ---- exclusion patterns (*must be last to be added*) ----
    # general patterns
    apidoc_command.extend([
        '*conftest*',
    ])

    # files/folders relative to `nucypher` project directory (results in required absolute paths)
    exclusion_items = [
        'setup.py',
        'tests',
        'scripts',
        Path('nucypher', 'utilities'),
        Path('nucypher', 'blockchain', 'eth', 'sol'),
        Path('nucypher', 'blockchain', 'eth', 'economics.py'),
        Path('nucypher', 'cli')
    ]
    for exclusion_item in exclusion_items:
        apidoc_command.append(f'{nucypher_module_dir / exclusion_item}')

    # ---- execute command ----
    apidoc.main(apidoc_command)


def run_solidity_apidoc(_):
    source_dir = Path(__file__).parent.resolve()
    scripts_dir = source_dir.parent.parent / 'scripts'

    install_script = scripts_dir / 'installation' / 'install_solc.py'
    subprocess.call(['python', str(install_script)])

    doc_script = scripts_dir / 'solidity_doc' / 'generate_doc.py'
    subprocess.call(['python', str(doc_script)])


def setup(app):
    app.add_css_file('style.css')
    app.connect("autodoc-process-docstring", remove_module_license)
    app.connect('builder-inited', run_apidoc)
    app.connect('builder-inited', run_solidity_apidoc)


add_module_names = False
autodoc_member_order = "bysource"


# -- Doctest configuration ----------------------------------------

import doctest

doctest_default_flags = (0
    | doctest.DONT_ACCEPT_TRUE_FOR_1
    | doctest.ELLIPSIS
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.NORMALIZE_WHITESPACE
)
