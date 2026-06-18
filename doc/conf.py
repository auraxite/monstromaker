# Файл конфигурации Sphinx.
#
# Полный список параметров:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Монстродел"
copyright = "2024, Монстродел Team"
author = "Монстродел Team"
release = "1.0.0"

extensions = [
	"sphinx.ext.autodoc",
	"sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

autodoc_default_options = {
	"members": True,
	"undoc-members": False,
	"show-inheritance": False,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
