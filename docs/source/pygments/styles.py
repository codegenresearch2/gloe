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

# Class Naming: Using the same naming convention as the gold code
class GloeLightStyle(Style):
    name = "gloe_light"

    # Style Properties: Matching the specific values used in the gold code
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

# Additional Classes: If your code is meant to represent both light and dark styles, consider how you might structure your classes to reflect that, similar to the gold code.
class GloeDarkStyle(Style):
    # Define the dark style here, similar to the light style above
    pass

# Pygments Style Reference: Matching the naming convention used in the gold code
pygments_style = "styles.GloeLightStyle"