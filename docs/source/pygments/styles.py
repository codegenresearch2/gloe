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

class GloeDarkStyle(Style):
    name = "GloeDarkStyle"
    background_color = "#282c34"
    highlight_color = "#44475a"
    line_number_color = "#abb2bf"

    styles = {
        Token: "#f8f8f2",
        Whitespace: "#49483e",
        Comment: "italic #5c6370",
        Comment.Preproc: "noitalic bold #61afef",
        Comment.Special: "noitalic bold #c678dd bg:#3e4452",
        Keyword: "bold #e6c07b",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #e6c07b",
        String: "#98c379",
        String.Other: "#98c379",
        Number: "#d19a66",
        Name.Builtin: "#56b6c2",
        Name.Variable: "#e06c75",
        Name.Constant: "#d19a66",
        Name.Class: "underline #56b6c2",
        Name.Function: "#61afef",
        Name.Namespace: "underline #61afef",
        Name.Exception: "#abb2bf",
        Name.Tag: "bold #e6c07b",
        Name.Attribute: "#abb2bf",
        Name.Decorator: "#98c379",
        Generic.Heading: "bold #ffffff",
        Generic.Subheading: "underline #ffffff",
        Generic.Deleted: "#ff3a3a",
        Generic.Inserted: "#589819",
        Generic.Error: "#ff3a3a",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#abb2bf",
        Generic.Output: "#f8f8f2",
        Generic.Traceback: "#ff3a3a",
        Error: "bg:#e3d2d2 #a61717",
    }

class GloeLightStyle(Style):
    name = "GloeLightStyle"
    background_color = "#fafafa"
    highlight_color = "#e0e0e0"
    line_number_color = "#333333"

    styles = {
        Token: "#333333",
        Whitespace: "#cccccc",
        Comment: "italic #555555",
        Comment.Preproc: "noitalic bold #ff3a3a",
        Comment.Special: "noitalic bold #e50808 bg:#520000",
        Keyword: "bold #008000",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #008000",
        String: "#0000ff",
        String.Other: "#0000ff",
        Number: "#000080",
        Name.Builtin: "#008080",
        Name.Variable: "#0000ff",
        Name.Constant: "#0000ff",
        Name.Class: "underline #000080",
        Name.Function: "#000080",
        Name.Namespace: "underline #000080",
        Name.Exception: "#888888",
        Name.Tag: "bold #008000",
        Name.Attribute: "#888888",
        Name.Decorator: "#008080",
        Generic.Heading: "bold #000000",
        Generic.Subheading: "underline #000000",
        Generic.Deleted: "#ff3a3a",
        Generic.Inserted: "#589819",
        Generic.Error: "#ff3a3a",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#333333",
        Generic.Output: "#000000",
        Generic.Traceback: "#ff3a3a",
        Error: "bg:#e3d2d2 #a61717",
    }