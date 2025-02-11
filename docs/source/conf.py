# Configuration file for the Sphinx documentation builder.
import os
import sys
from pygments.style import Style
from pygments.token import Token, Whitespace, Comment, Keyword, Operator, String, Number, Name, Generic, Error

# Project information
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("pygments"))
project = "Gloe"
copyright = "2023, Samir Braga"
author = "Samir Braga"
release = "0.4.3"

# General configuration
extensions = [
    "sphinx_toolbox.more_autodoc.variables",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph",
    "myst_parser",
    "sphinx_copybutton",
]
napoleon_google_docstring = True
autosectionlabel_prefix_document = True
intersphinx_mapping = {"httpx": ("https://www.python-httpx.org/", None)}
ogp_site_url = "https://gloe.ideos.com.br/"
ogp_image = "https://gloe.ideos.com.br/_static/assets/gloe-logo.png"

# HTML output configuration
html_title = "Gloe"
html_theme = "furo"
html_sidebars = {"Home": ["/"]}
html_static_path = ["_static"]
html_css_files = ["theme_customs.css"]
html_favicon = "_static/assets/favicon.ico"
html_theme_options = {
    "light_logo": "assets/gloe-logo-small.png",
    "dark_logo": "assets/gloe-logo-small.png",
    "dark_css_variables": {
        "color-brand-primary": "#00e6bf",
        "color-brand-content": "#00e6bf",
        "font-stack": "Roboto, sans-serif",
        "font-stack--monospace": "Courier, monospace",
        "font-size--normal": "Courier, monospace",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/ideos/gloe",
            "html": """<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">...</svg>""",
        },
    ],
}

# Pygments style configuration
class GloeLightStyle(Style):
    name = "gloe-light"
    background_color = "#ffffff"
    highlight_color = "#404040"
    line_number_color = "#aaaaaa"
    styles = {
        Token: "#d0d0d0",
        Whitespace: "#666666",
        Comment: "italic #ababab",
        Comment.Preproc: "noitalic bold #ff3a3a",
        Comment.Special: "noitalic bold #e50808 bg:#520000",
        Keyword: "bold #45df9a",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #45df9a",
        String: "#6ad7ca",
        String.Other: "#6ad7ca",
        Number: "#51b2fd",
        Name.Builtin: "#2fbccd",
        Name.Variable: "#40ffff",
        Name.Constant: "#40ffff",
        Name.Class: "underline #14c8ef",
        Name.Function: "#14c8ef",
        Name.Namespace: "underline #14c8ef",
        Name.Exception: "#bbbbbb",
        Name.Tag: "bold #45df9a",
        Name.Attribute: "#bbbbbb",
        Name.Decorator: "#6ad7ca",
        Generic.Heading: "bold #ffffff",
        Generic.Subheading: "underline #ffffff",
        Generic.Deleted: "#ff3a3a",
        Generic.Inserted: "#589819",
        Generic.Error: "#ff3a3a",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#aaaaaa",
        Generic.Output: "#cccccc",
        Generic.Traceback: "#ff3a3a",
        Error: "bg:#e3d2d2 #a61717",
    }

pygments_style = "styles.GloeLightStyle"