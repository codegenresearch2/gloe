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
    line_number_color = "#61afef"

    styles = {
        Token: "#f8f8f2",
        Whitespace: "#49483e",
        Comment: "italic #6272a4",
        Comment.Preproc: "noitalic bold #f1fa8c",
        Comment.Special: "noitalic bold #ff79c6 bg:#44475a",
        Keyword: "bold #8be9fd",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #8be9fd",
        String: "#f1fa8c",
        String.Other: "#f1fa8c",
        Number: "#bd93f9",
        Name.Builtin: "#50fa7b",
        Name.Variable: "#f8f8f2",
        Name.Constant: "#f8f8f2",
        Name.Class: "underline #ffb86c",
        Name.Function: "#ffb86c",
        Name.Namespace: "underline #ffb86c",
        Name.Exception: "#ff79c6",
        Name.Tag: "bold #ff79c6",
        Name.Attribute: "#f8f8f2",
        Name.Decorator: "#50fa7b",
        Generic.Heading: "bold #f8f8f2",
        Generic.Subheading: "underline #f8f8f2",
        Generic.Deleted: "#ff5555",
        Generic.Inserted: "#50fa7b",
        Generic.Error: "#ff5555",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#6272a4",
        Generic.Output: "#f8f8f2",
        Generic.Traceback: "#ff5555",
        Error: "bg:#ff5555 #f8f8f2",
    }

class GloeLightStyle(Style):
    name = "GloeLightStyle"
    background_color = "#f8f8f8"
    highlight_color = "#e6e6e6"
    line_number_color = "#333333"

    styles = {
        Token: "#282a36",
        Whitespace: "#bbbbbb",
        Comment: "italic #44475a",
        Comment.Preproc: "noitalic bold #f1fa8c",
        Comment.Special: "noitalic bold #ff79c6 bg:#e6e6e6",
        Keyword: "bold #005cc5",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #005cc5",
        String: "#008000",
        String.Other: "#008000",
        Number: "#000080",
        Name.Builtin: "#008080",
        Name.Variable: "#282a36",
        Name.Constant: "#282a36",
        Name.Class: "underline #005cc5",
        Name.Function: "#005cc5",
        Name.Namespace: "underline #005cc5",
        Name.Exception: "#ff79c6",
        Name.Tag: "bold #005cc5",
        Name.Attribute: "#282a36",
        Name.Decorator: "#008080",
        Generic.Heading: "bold #282a36",
        Generic.Subheading: "underline #282a36",
        Generic.Deleted: "#ff5555",
        Generic.Inserted: "#008000",
        Generic.Error: "#ff5555",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#44475a",
        Generic.Output: "#282a36",
        Generic.Traceback: "#ff5555",
        Error: "bg:#ff5555 #282a36",
    }