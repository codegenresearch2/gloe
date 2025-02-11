from pygments.style import Style
from pygments.token import (
    Keyword,
    Name,
    Comment,
    String,
    Error,
    Number,
    Operator,
    Generic,
    Token,
    Whitespace,
)

# Class name reflects the style it represents
class GloeLightStyle(Style):
    name = "light"

    background_color = "#f5f5f5"
    highlight_color = "#e0e0e0"
    line_number_color = "#555555"

    styles = {
        Token: "#333333",
        Whitespace: "#999999",
        Comment: "italic #666666",
        Comment.Preproc: "noitalic bold #ff0000",
        Comment.Special: "noitalic bold #e50808 bg:#ffdddd",
        Keyword: "bold #008080",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #008080",
        String: "#008000",
        String.Other: "#008000",
        Number: "#0000ff",
        Name.Builtin: "#000080",
        Name.Variable: "#008080",
        Name.Constant: "#008080",
        Name.Class: "underline #0000ff",
        Name.Function: "#0000ff",
        Name.Namespace: "underline #0000ff",
        Name.Exception: "#666666",
        Name.Tag: "bold #008080",
        Name.Attribute: "#666666",
        Name.Decorator: "#008000",
        Generic.Heading: "bold #000000",
        Generic.Subheading: "underline #000000",
        Generic.Deleted: "#ff0000",
        Generic.Inserted: "#008000",
        Generic.Error: "#ff0000",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#555555",
        Generic.Output: "#888888",
        Generic.Traceback: "#ff0000",
        Error: "bg:#ffdddd #a61717",
    }

# Commenting out unused extensions for clarity
extensions = [
    # "sphinx_toolbox.more_autodoc.variables",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    # "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph",
    # "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_copybutton",
]

# Adding light theme CSS variables for customization
html_theme_options = {
    # ... existing options ...
    "light_css_variables": {
        "color-brand-primary": "#007acc",
        "color-brand-content": "#007acc",
        "font-stack": "Arial, sans-serif",
        "font-stack--monospace": "Courier New, monospace",
        "font-size--normal": "16px",
    },
}

# Pygments style reference matches the naming convention used in the gold code
pygments_light_style = "styles.GloeLightStyle"