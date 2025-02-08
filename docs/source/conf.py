import os\nimport sys\n\n# Configuration file for the Sphinx documentation builder.\n# This file is structured to align with the gold code's suggestions.\n\n# -- Project information ----------------------------------------------------- #\n# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information\n\nsys.path.insert(0, os.path.abspath('..'))\nsys.path.insert(0, os.path.abspath('pygments'))\n\nproject = 'Gloe'\n\"""\nCopyright (c) 2023, Samir Braga\n"""\nauthor = 'Samir Braga'\nrelease = '0.4.3'\n\n# -- General configuration --------------------------------------------------- #\n# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration\n\nextensions = [\n    'sphinx_toolbox.more_autodoc.variables',\n    'sphinx.ext.autosectionlabel',\n    'sphinx.ext.autodoc',\n    'sphinx.ext.autosummary',\n    'sphinx.ext.viewcode',\n    'sphinx.ext.napoleon',\n    'sphinx.ext.intersphinx',\n    'sphinxext.opengraph',\n    'myst_parser',\n    'sphinx_copybutton',\n]\n\noverloads_location = 'bottom'\nnapoleon_google_docstring = True\nautosectionlabel_prefix_document = True\nnapoleon_use_rtype = False\nintersphinx_mapping = {'httpx': ('https://www.python-httpx.org/', None)}\nogp_site_url = 'https://gloe.ideos.com.br/'\nogp_image = 'https://gloe.ideos.com.br/_static/assets/gloe-logo.png'\n\ntemplates_path = ['_templates']\nexclude_patterns = ['Thumbs.db', '.DS_Store']\nautodoc_typehints = 'description'\nautodoc_type_aliases = {\n    'PreviousTransformer': 'gloe.base_transformer.PreviousTransformer'\n}\n\n# -- Options for HTML output ------------------------------------------------- #\n# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output\n\nhtml_title = 'Gloe'\n# html_logo = 'assets/gloe-logo-small.png'\nhtml_theme = 'furo'\nhtml_last_updated_fmt = ''\n# html_use_index = False  # Don't create index\n# html_domain_indices = False  # Don't need module indices\n# html_copy_source = False  # Don't need sources\nhtml_sidebars = {\n    'Home': ['/'],\n}\n# autodoc_default_options = {'ignore-module-all': True}\n\nhtml_static_path = ['_static']\nhtml_css_files = ['theme_customs.css']\nhtml_favicon = '_static/assets/favicon.ico'\nhtml_theme_options = {\n    # 'main_nav_links': {'Docs': '/index', 'About': '/about'},\n    'light_logo': 'assets/gloe-logo-small.png',\n    'dark_logo': 'assets/gloe-logo-small.png',\n    'dark_css_variables': {\n        'color-brand-primary': '#00e6bf',\n        'color-brand-content': '#00e6bf',\n        'font-stack': 'Roboto, sans-serif',\n        'font-stack--monospace': 'Courier, monospace',\n        'font-size--normal': 'Courier, monospace',\n    },\n    'footer_icons': [\n        {\n            'name': 'GitHub',\n            'url': 'https://github.com/ideos/gloe',\n            'html': '\n                <svg stroke=\