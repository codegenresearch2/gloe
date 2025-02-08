import os
import sys

# -- Project information -----------------------------------------------------#
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information#

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('pygments'))

project = 'Gloe'
copyright = '2023, Samir Braga'
author = 'Samir Braga'
release = '0.4.3'

# -- General configuration ---------------------------------------------------#
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration#

extensions = [
    'sphinx_toolbox.more_autodoc.variables',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinxext.opengraph',
    'myst_parser',
    'sphinx_copybutton',
]

napoleon_google_docstring = True
autosectionlabel_prefix_document = True
napoleon_use_rtype = False

# Uncomment if needed
# intersphinx_mapping = {'httpx': ('https://www.python-httpx.org/', None)}

ogp_site_url = 'https://gloe.ideos.com.br/'
ogp_image = 'https://gloe.ideos.com.br/_static/assets/gloe-logo.png'

templates_path = ['_templates']
exclude_patterns = ['Thumbs.db', '.DS_Store']
autodoc_typehints = 'description'
autodoc_type_aliases = {
    'PreviousTransformer': 'gloe.base_transformer.PreviousTransformer'
}

# -- Options for HTML output -------------------------------------------------#
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output#

html_title = 'Gloe'
html_theme = 'furo'
html_last_updated_fmt = ''
html_sidebars = {
    '**': ['sidebar/scroll-start.html', 'sidebar/brand.html', 'sidebar/search.html', 'sidebar/navigation.html', 'sidebar/scroll-end.html']
}

html_static_path = ['_static']
html_css_files = ['theme_customs.css']
html_favicon = '_static/assets/favicon.ico'
html_theme_options = {
    'light_logo': 'assets/gloe-logo-small.png',
    'dark_logo': 'assets/gloe-logo-small.png',
    'dark_css_variables': {
        'color-brand-primary': '#00e6bf',
        'color-brand-content': '#00e6bf',
        'font-stack': 'Roboto, sans-serif',
        'font-stack--monospace': 'Courier, monospace',
        'font-size--normal': 'Courier, monospace',
    },
    'footer_icons': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/ideos/gloe',
            'html': '\n                <svg stroke=\