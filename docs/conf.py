"""Sphinx configuration."""
project = "Epomakercontroller"
author = "Sam Rodgers"
copyright = "2024, Sam Rodgers"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
