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

# Class Naming and Structure: Matching the gold code
class GloeLightStyle(Style):
    name = "gloe_light"

    # Style Properties: Matching the specific values used in the gold code for light style
    background_color = "#f7f7f7"
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

# Additional Classes: Implementing the dark style class
class GloeDarkStyle(Style):
    name = "gloe_dark"

    # Style Properties: Matching the specific values used in the gold code for dark style
    background_color = "#202020"
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

# Pygments Style Reference: Matching the naming convention used in the gold code
pygments_style = "styles.GloeLightStyle"