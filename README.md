# toolbox_creator
A small library to enable the fast creation of Graphical User Interfaces for python based toolboxes.

Bring you python API to the masses, easily and convinently. 

    pip install toolbox-creator-CFI
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple toolbox-creator-CFI

## Features:
* Create a toolbox from your python library fast
* Cross platform GUI
* Python native
* Bundle to .exe, .dmg or .bin using pyinstaller
* Built on PySimpleGUI

An executable can be created through pyinstaller like so:

    pyinstaller -wF --noconfirm --clean --noconsole --icon=path_to_ico_file path_to_gui_script.py
    pyinstaller -wF --noconfirm --clean --noconsole --icon=./globe_icon.ico gui.py

On windows, it is necessary to wrap the function to ensure it forks the process correctly.
It is currently only possible to have one function window open at a time on Windows. This will be fixed in a future release.
multiple windows can be enabled by setting run_subprocess=True
```python
def main():
    tools = {} # define tools here.
    create_gui(tools, create_console=True)

if __name__ == "__main__":
    main()
```

## Supports the following input types
### file_open
Opens a file dialog to select a single file.
### file_save
Opens a file dialog to save a single file. File types can be specified.
### file_open_multiple
Opens a file dialog and enable the selection of multiple files.
### folder_open
Opens a dialog to enable the selection of a folder.
### folder_save
Same as folder_open.
### number
Create a number input field. Only integers and floats are allowed. Minimum and maximim values can be specified.
```python
{
    "a_parameter_taking_a_number": {
        "type": "number",
        "min_value": 0, # Optional. Default: -inf
        "max_value": 100, # Optional. Default: +inf
    }
}
```
### string, password
Create a string or password input field. Password is the same as string, but the input is hidden in the display.
```python
{
    "a_parameter_taking_a_string": {
        "type": "string", # Or type: "password" for hidden characters
        "min_length": 1, # Optional. Default: 0
        "max_length": 100, # Optional. Default: =inf
    }
}
```

### boolean
Create a bolean input field. Output will be True or False.
```python
{
    "a_parameter_taking_a_bool": {
        "type": "boolean",
        "default": True, # Optional. Default: False
    }
}
```
### radio
Create a radio input field. Must have multiple values and one default value.
```python
{
    "a_parameter_with_radio_options": {
        "type": "radio",
        "options": [
            {
                "label": "Windows (\\r\\n)",
                "key": "windows",
                "value": "\r\n",
                "default": True, # Default option must be specified.
            },
            {
                "label": "Unix (\\n)",
                "key": "linux",
                "value": "\n",
            },
            {
                "label": "Mac (\\r)",
                "key": "macos",
                "value": "\r",
            },
        ],
    }
}
```
### dropdown
Creates a drop down field of multiple values.
```python
{
    "a_parameter_with_dropdown_options": {
        "type": "dropdown",
        "options": [
            {"label": "Commas (,)", "value": ",", "default": True}, # Default option must be specifed.
            {"label": "Spaces ( )", "value": " "},
            {"label": "Semicolons (;)", "value": ";"},
            {"label": "Other..", "value": "other"},
        ],
    }
},
```
### slider
Creates a horisontal slider field for numerical values. Min, max, and step values can be specified.
```python
{
    "a_parameter_with_a_numerical_value_as_input": {
        "type": "slider",
        "min_value": 0,
        "max_value": 100,
        "step": 1,
    }
}
```
### date_year
Creates a date selector. Output of selection is in the format yyyymmdd
```python
{
    "a_parameter_taking_a_date_as_input": {
        "type": "date_year",
        "default": "days_ago_14", # optional. Default: "today". options are: days_ago_x, today, or a specific date
    }
},
```

These options are available for all input types.
```python
"display_name": "Parameter name",                   # The parameter name to show in the toolbox.
"default": 100,                                     # Default value.
"keyword": True,                                    # Pass parameter as arg or kwarg. Default arg.
"tooltip": "This tooltip is displayed on hover",    # Tooltip to display on hover.
"enabled_by": {"other_parameter": ["value"]},       # If other parameter has value. Show parameter, otherwise hide.
```` 

# Example use

![Screenshot showing the tool selection menu](https://github.com/casperfibaek/toolbox-gui/raw/main/screenshot_main.jpg "Select tool")


## First create or import a function to add:
```python
import os

def add_line_to_csv(file_path, line, linebreak="\n"):
    """ Add a line to a CSV file. """
    try:
        with open(file_path, "a") as file:
            file.write(line + linebreak)
        return 1
    except:
        return 0


# Example function to run
def create_dummy_csv_file(
    name,
    folder,
    cols=1,
    rows=1,
    seperator=",",
    other_seperator=None,
    linebreak="\n",
    include_header=True,
    metadata_date="today",
    prefix="",
    postfix="",
    verbose=False,
):
    """
    Creates a dummy csv file with rows and cols. Not very useful, but it's a good example.
    """
    file_path = os.path.join(folder, prefix + name + postfix + ".csv")

    if other_seperator is not None:
        seperator = other_seperator

    row = ("example" + seperator) * cols

    with open(file_path, "w") as file:
        file.write("")

    if include_header:
        header = ("header" + seperator) * cols
        add_line_to_csv(os.path.join(folder, file_path), header, linebreak)

    for _ in range(rows):
        add_line_to_csv(os.path.join(folder, file_path), row, linebreak)

    if verbose:
        print(f"Created file: {file_path} on {metadata_date}")

    return file_path
```

## Then define the parameters of the tools:
```python
tools = {}

tools["Create CSV Simple"] = {
    "description": "Creates a new empty CSV file.",
    "function": create_dummy_csv_file,
    "parameters": [
        {
            "name": {
                "type": "string",
                "display_name": "File Name",                        # Optional. Default: parameter name
                "default": "",                                      # Optional. Default: ""
                "tooltip": "The name of the csv file to create.",   # Optional. Default: ""
            }
        },
        {
            "out_folder": {
                "type": "folder_open",
                "display_name": "Out Folder",                           # Optional. Default: parameter name
                "tooltip": "The path to folder to save the CSV file.",  # Optional. Default: ""
            }
        },
    ],
}
```

![Screenshot showing the function menu for the simple example tool.](https://github.com/casperfibaek/toolbox-gui/raw/main/screenshot_function_simple.jpg "Simple tool selected")

```python

tools["Create CSV Advanced"] = {
    "description": "Creates a new empty CSV file. (Advanced method.)",
    "function": create_csv_file,
    "parameters": [
        {
            "name": {
                "type": "string",
                "display_name": "File Name",                        # Optional. Default: parameter name
                "default": "new_csv_file",                          # Optional. Default: ""
                "min_length": 1,                                    # Optional. Default: 0
                "tooltip": "The name of the csv file to create.",   # Optional. Default: ""
            }
        },
        {
            "out_folder": {
                "type": "folder_open",
                "display_name": "Out Folder",                           # Optional. Default: parameter name
                "tooltip": "The path to folder to save the CSV file.",  # Optional. Default: ""
            }
        },
        {
            "cols": {
                "type": "number",
                "min_value": 0,
                "max_value": 100,
                "display_name": "Number of Columns",                    # Optional. Default: parameter name
                "default": 1,                                           # Optional. Default: 0
                "keyword": True,                                        # Optional. Default: False
                "tooltip": "The number of columns in the CSV file.",    # Optional. Default: ""
            }
        },
        {
            "rows": {
                "type": "slider",
                "min_value": 0,
                "max_value": 100,
                "step": 1,
                "display_name": "Number of Rows",                   # Optional. Default: parameter name
                "default": 1,                                       # Optional. Default: min_value
                "keyword": True,                                    # Optional. Default: False
                "tooltip": "The number of rows in the CSV file.",   # Optional. Default: ""
            }
        },
        {
            "seperator": {
                "type": "dropdown",
                "options": [
                    {"label": "Commas (,)", "value": ",", "default": True},
                    {"label": "Tabs (  )", "value": "\t"},
                    {"label": "Spaces ( )", "value": " "},
                    {"label": "Semicolons (;)", "value": ";"},
                    {"label": "Colons (:)", "value": ":"},
                    {"label": "Dashes (-)", "value": "-"},
                    {"label": "Underscores (_)", "value": "_"},
                    {"label": "Dots (.)", "value": "."},
                    {"label": "Bars (|)", "value": "|"},
                    {"label": "Other..", "value": "other"},
                ],
                "display_name": "Seperator",                            # Optional. Default: parameter name
                "keyword": True,                                        # Optional. Default: False
                "tooltip": "The seperator to use in the CSV file.",     # Optional. Default: ""
            }
        },
        {
            "other_seperator": {
                "type": "string",
                "display_name": "Other Seperator",                      # Optional. Default: parameter name
                "max_length": 4,                                        # Optional. Default: +inf
                "default": ",",                                         # Optional. Default: ""
                "enabled_by": {"seperator": ["other"]},                 # Optional. Default: None
                "keyword": True,                                        # Optional. Default: False
                "tooltip": "The seperator to use in the CSV file.",     # Optional. Default: ""
            }
        },
        {
            "metadata_date": {
                "type": "date_year",
                "display_name": "Metadata Date",                # Optional. Default: parameter name
                "default": "today",                             # optional. Default: "today". options are: days_ago_x, today, or a specific date
                "keyword": True,                                # Optional. Default: False
                "tooltip": "The date to use in the metadata.",  # Optional. Default: ""
            }
        },
        {
            "include_header": {
                "type": "boolean",
                "display_name": "Include Header",                       # Optional. Default: parameter name
                "default": True,                                        # Optional. Default: False
                "keyword": True,                                        # Optional. Default: False
                "tooltip": "Include a header row in the CSV file.",     # Optional. Default: ""
            }
        },
        {
            "linebreak": {
                "type": "radio",
                "options": [
                    {
                        "label": "Windows (\\r\\n)",
                        "key": "windows",
                        "value": "\r\n",
                        "default": True,
                    },
                    {"label": "Unix (\\n)", "key": "linux", "value": "\n"},
                    {"label": "Mac (\\r)", "key": "macos", "value": "\r"},
                ],
                "display_name": "Linebreak",                            # Optional. Default: parameter name
                "tooltip": "The linebreak to use in the CSV file.",     # Optional. Default: ""
                "keyword": True,                                        # Optional. Default: False
            }
        },
        {
            "prefix": {
                "type": "string",
                "display_name": "Prefix",                       # Optional. Default: parameter name
                "default": "",                                  # Optional. Default: ""
                "keyword": True,                                # Optional. Default: False
                "tooltip": "Prefix to add to the file name.",   # Optional. Default: ""
            }
        },
        {
            "postfix": {
                "type": "string",
                "display_name": "Postfix",                      # Optional. Default: parameter name
                "default": "",                                  # Optional. Default: ""
                "keyword": True,                                # Optional. Default: False
                "tooltip": "Postfix to add to the file name.",  # Optional. Default: ""
            }
        },
    ],
}

if __name__ == "__main__":
    from toolbox_creator.gui import create_gui

    create_gui(tools, name="Example Toolbox")
```

![Screenshot showing the function menu for the advanced example tool.](https://github.com/casperfibaek/toolbox-gui/raw/main/screenshot_function_advanced.jpg "Advanced tool selected")

## Built and distribute
python -m build

python -m twine upload --repository testpypi dist/*