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
    background_color = "#202020"
    highlight_color = "#404040"

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

class GloeLightStyle(Style):
    name = "GloeLightStyle"
    background_color = "#ffffff"
    highlight_color = "#f0f0f0"

    styles = {
        Token: "#333333",
        Whitespace: "#999999",
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
        Name.Class: "underline #0000ff",
        Name.Function: "#0000ff",
        Name.Namespace: "underline #0000ff",
        Name.Exception: "#808080",
        Name.Tag: "bold #008000",
        Name.Attribute: "#808080",
        Name.Decorator: "#0000ff",
        Generic.Heading: "bold #000000",
        Generic.Subheading: "underline #000000",
        Generic.Deleted: "#ff3a3a",
        Generic.Inserted: "#589819",
        Generic.Error: "#ff3a3a",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#555555",
        Generic.Output: "#333333",
        Generic.Traceback: "#ff3a3a",
        Error: "bg:#e3d2d2 #a61717",
    }