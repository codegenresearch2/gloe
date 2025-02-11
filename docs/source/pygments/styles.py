# Class for the dark theme
class GloeDarkStyle:
    name = "GloeDarkStyle"

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

# Class for the light theme
class GloeLightStyle:
    name = "GloeLightStyle"

    background_color = "#ffffff"
    highlight_color = "#f0f0f0"
    line_number_color = "#555555"

    styles = {
        Token: "#333333",
        Whitespace: "#cccccc",
        Comment: "italic #555555",
        Comment.Preproc: "noitalic bold #3a3aff",
        Comment.Special: "noitalic bold #3a3aff bg:#e0e0ff",
        Keyword: "bold #008080",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #008080",
        String: "#008000",
        String.Other: "#008000",
        Number: "#0000FF",
        Name.Builtin: "#008080",
        Name.Variable: "#0000FF",
        Name.Constant: "#0000FF",
        Name.Class: "underline #0000FF",
        Name.Function: "#0000FF",
        Name.Namespace: "underline #0000FF",
        Name.Exception: "#888888",
        Name.Tag: "bold #008080",
        Name.Attribute: "#888888",
        Name.Decorator: "#008080",
        Generic.Heading: "bold #000000",
        Generic.Subheading: "underline #000000",
        Generic.Deleted: "#FF0000",
        Generic.Inserted: "#00FF00",
        Generic.Error: "#FF0000",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.EmphStrong: "bold italic",
        Generic.Prompt: "#555555",
        Generic.Output: "#000000",
        Generic.Traceback: "#FF0000",
        Error: "bg:#FFCCCC #800000",
    }


This new code snippet addresses the feedback by creating separate classes for the dark and light themes, ensuring the `name` attribute matches the naming convention, and setting the appropriate properties for each theme.