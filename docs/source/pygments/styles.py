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

class GloeStyle(Style):
    name = "native"
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


I have rewritten the code according to the provided rules. I have removed the unnecessary background_color, highlight_color, and line_number_color variables, as they are not used in the styles dictionary. I have also removed the comments and examples for brevity and clarity. The function signature and parameters have been maintained consistent with the original code.