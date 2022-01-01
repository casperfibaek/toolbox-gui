import os
import inspect
import PySimpleGUIQt as sg
from toolbox_creator.utils import (
    get_args,
    get_first_key,
    add_slash_to_end,
    get_param_name,
    default_texts,
)


def validate_inputs(function_name, values_func, window, tools):
    validation = validate_input(function_name, values_func, tools)

    for idx, input_param_name in enumerate(validation["names"]):
        input_param_key = input_param_name + "_text"

        if validation["valid"][idx] == False:
            window[input_param_key].update(background_color="#cfa79d")
        else:
            window[input_param_key].update(background_color=sg.theme_background_color())

    return validation


def validate_type(input_type, input_value, name, tool_name, tools):
    valid = False
    keyword = False
    cast = None
    message = ""

    _func_args, func_keywords = get_args(tools[tool_name]["function"])

    func_params = tools[tool_name]["parameters"]
    definition = False
    for func_param in func_params:
        if name in func_param.keys():
            definition = func_param[name]
            break

    if definition is not False and "keyword" in definition.keys():
        keyword = definition["keyword"]

        if keyword and name not in func_keywords:
            raise Exception(
                f"{tool_name} has a keyword {name} that the function {tool_name} does not take."
            )

    if input_type == "file_open":
        if isinstance(input_value, str) and os.path.isfile(input_value):
            valid = True
            cast = input_value
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid file."

    elif input_type == "file_open_multiple":
        if (
            isinstance(input_value, str)
            and len(input_value) > 0
            and len(input_value.split(";")) > 0
            and all(os.path.isfile(i) for i in input_value.split(";"))
        ):
            valid = True
            cast = input_value.split(";")
        else:
            valid = False
            message = f"{name}: {input_value} contains invalid files."

    elif input_type == "folder_save" or input_type == "folder_open":
        if (
            isinstance(input_value, str)
            and len(input_value) > 2  # "./"
            and os.path.isdir(input_value)
        ):
            valid = True
            cast = add_slash_to_end(input_value)
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid folder."

    elif input_type == "file_save":
        if isinstance(input_value, str) and os.path.isdir(os.path.dirname(input_value)):
            valid = True
            cast = input_value
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid save destination."

    elif input_type == "number":
        if (
            isinstance(input_value, int)
            or isinstance(input_value, float)
            or isinstance(input_value, str)
        ):
            try:
                cast = float(input_value)
                if cast.is_integer():
                    cast = round(cast)

                valid = True

                if "min_value" in definition.keys() and cast < definition["min_value"]:
                    valid = False
                    message = f"{name}: {input_value} is less than the minimum value of {definition['min_value']}."
                elif (
                    "max_value" in definition.keys() and cast > definition["max_value"]
                ):
                    valid = False
                    message = f"{name}: {input_value} is higher than the maximum value of {definition['max_value']}."
            except:
                valid = False
                message = f"{name}: {input_value} is not a valid number."
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid number."

    elif input_type == "boolean":
        if isinstance(input_value, bool):
            valid = True
            cast = input_value
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid boolean."

    elif input_type == "radio":
        if definition:
            options = definition["options"]
            for button in input_value:
                if True in button.values():
                    button_key = get_first_key(button)[len(name) + 1 :]
                    break

            for option in options:
                if option["key"] == button_key:
                    cast = option["value"]
                    valid = True
                    break

        else:
            valid = False
            message = f"{name}: {input_value} is defined poorly in tools.."

    elif input_type == "dropdown":
        if definition:
            options = definition["options"]

        for option in options:
            if option["label"] == input_value:
                cast = option["value"]
                valid = True
                break

    elif input_type == "slider":
        try:
            cast = float(input_value)
            if cast.is_integer():
                cast = round(cast)

            if "min_value" in definition.keys() and cast < definition["min_value"]:
                valid = False
                message = f"{name}: {input_value} is below the minimum value of {definition['min_value']}."
            elif "max_value" in definition.keys() and cast > definition["max_value"]:
                valid = False
                message = f"{name}: {input_value} is above the maximum value of {definition['max_value']}."
            else:
                valid = True
        except:
            valid = False
            message = f"{name}: {input_value} is not a valid number."

    elif input_type == "string" or "password":
        if isinstance(input_value, str):
            valid = True
            cast = input_value

            if (
                "min_length" in definition.keys()
                and len(input_value) < definition["min_length"]
            ):
                valid = False
                min_chars = definition["min_length"]
                message = f"{name}: {input_value} is not a valid string. String too short. Min chars: {min_chars}."

            if (
                "max_length" in definition.keys()
                and len(input_value) > definition["max_length"]
            ):
                valid = False
                max_chars = definition["max_length"]
                message = f"{name}: {input_value} is not a valid string. String too long. Max chars: {max_chars}"
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid string."
    elif input_type == "date_year":
        if isinstance(input_value, str) and len(input_value) == 8:
            valid = True
            cast = input_value
        else:
            valid = False
            message = f"{name}: {input_value} is not a valid date (yyyymmdd)."
    else:
        valid = False
        message = f"{name}: {input_value} is not a valid type."

    return valid, cast, message, keyword


def validate_input(tool_name, parameters, tools):
    ret_obj = {
        "valid": [],
        "cast_args": [],
        "cast_kwargs": {},
        "cast": [],
        "message": [],
        "names": [],
    }

    for tool_params in tools[tool_name]["parameters"]:
        name = get_param_name(tool_params)
        input_type = tool_params[name]["type"]

        if input_type == "radio":
            input_value = []
            for key in parameters.keys():
                if name == key[: len(name)]:
                    input_value.append({key: parameters[key]})
        else:
            input_value = parameters[name]

        if isinstance(input_value, str) and input_value in default_texts:
            valid = False
            cast = None
            message = f"No file/folder selected for {name}."
            keyword = False
        else:
            valid, cast, message, keyword = validate_type(
                input_type,
                input_value,
                name,
                tool_name,
                tools,
            )

        ret_obj["valid"].append(valid)
        ret_obj["message"].append(message)
        ret_obj["names"].append(name)

        if keyword:
            ret_obj["cast_kwargs"][name] = cast
        else:
            ret_obj["cast_args"].append(cast)

        ret_obj["cast"].append(cast)

    return ret_obj


def update_inputs(event, values, window, listeners, function_name, tools):
    validated = None
    for listener in listeners:
        if listener["enabled_by"] == event:
            if validated is None:
                validated = validate_input(function_name, values, tools)

            for idx in range(len(validated["names"])):
                name = validated["names"][idx]
                value = validated["cast"][idx]

                if name != event:
                    continue

                param_name = listener["parameter"]
                if value not in listener["values"]:
                    window[param_name + "_col1"].Update(visible=False)
                    window[param_name + "_col2"].Update(visible=False)
                else:
                    window[param_name + "_col1"].Update(visible=True)
                    window[param_name + "_col2"].Update(visible=True)

    window.refresh()


def validate_parameter(parameter, args):
    parameter_types = [
        "file_open",
        "file_save",
        "file_open_multiple",
        "number",
        "boolean",
        "radio",
        "dropdown",
        "slider",
        "string",
        "password",
        "date_year",
        "folder_open",
        "folder_save",
    ]

    errors = []

    param_name = get_param_name(parameter)
    param_options = parameter[param_name]

    if "type" not in param_options.keys():
        errors.append(f"{param_name}: missing type.")
    elif param_options["type"] not in parameter_types:
        errors.append(
            f"{param_name}: {param_options['type']} is not a valid type. Valid types are: {parameter_types}"
        )
    else:
        if param_options["type"] == "slider":
            if "min_value" not in param_options.keys():
                errors.append(f"{param_name}: missing min_value.")
            elif "max_value" not in param_options.keys():
                errors.append(f"{param_name}: missing max_value.")
            elif "step" not in param_options.keys():
                errors.append(f"{param_name}: missing step.")
            elif not isinstance(param_options["min_value"], (int, float)):
                errors.append(f"{param_name}: min_value is not a number.")
            elif not isinstance(param_options["max_value"], (int, float)):
                errors.append(f"{param_name}: max_value is not a number.")
            elif param_options["min_value"] >= param_options["max_value"]:
                errors.append(f"{param_name}: min_value must be less than max.")

        if param_options["type"] == "radio":
            if "options" not in param_options.keys():
                errors.append(f"{param_name}: missing options.")
            else:
                default_found = False
                for idx, option in enumerate(param_options["options"]):
                    if "label" not in option.keys():
                        errors.append(
                            f"{param_name}: missing label for option {idx + 1}."
                        )
                    elif "value" not in option.keys():
                        errors.append(
                            f"{param_name}: missing value for option {idx + 1}."
                        )
                    elif "key" not in option.keys():
                        errors.append(
                            f"{param_name}: missing key for option {idx + 1}."
                        )

                    if "default" in option.keys() and option["default"]:
                        if default_found is True:
                            errors.append(
                                f"{param_name}: multiple default options found."
                            )
                        else:
                            default_found = True

                if default_found is False:
                    errors.append(
                        f"{param_name}: no default option found, please set one radio button as default."
                    )

                if len(param_options["options"]) < 2:
                    errors.append(
                        f"{param_name}: radio options must have at least 2 options."
                    )

        if param_options["type"] == "dropdown":
            if "options" not in param_options.keys():
                errors.append(f"{param_name}: missing options.")
            else:
                default_found = False
                for idx, option in enumerate(param_options["options"]):
                    if "label" not in option.keys():
                        errors.append(
                            f"{param_name}: missing label for option {idx + 1}."
                        )
                    elif "value" not in option.keys():
                        errors.append(
                            f"{param_name}: missing value for option {idx + 1}."
                        )

                    if "default" in option.keys() and option["default"]:
                        if default_found is True:
                            errors.append(
                                f"{param_name}: multiple default options found."
                            )
                        else:
                            default_found = True

                if default_found is False:
                    errors.append(
                        f"{param_name}: no default option found, please set one radio button as default."
                    )

                if len(param_options["options"]) < 2:
                    errors.append(
                        f"{param_name}: dropdown options must have at least 2 options."
                    )

    if "display_name" not in param_options.keys():
        errors.append(f"{param_name}: missing display_name.")
    else:
        if not isinstance(param_options["display_name"], str):
            errors.append(
                f"{param_name}: {param_options['display_name']} is not a valid display_name."
            )
        elif len(param_options["display_name"]) == 0:
            errors.append(
                f"{param_name}: {param_options['display_name']} is not a valid display_name. Length can't be zero."
            )
        elif len(param_options["display_name"]) > 26:
            errors.append(
                f"{param_name}: {param_options['display_name']} is not a valid display_name. Length can't be greater than 26. Currently: {len(param_options['display_name'])}"
            )

    args, kwargs = args
    if "keyword" in param_options.keys() and param_options["keyword"]:
        if param_name not in kwargs:
            errors.append(
                f"{param_name} specified as a keyword argument, but the function takes no keyword argument of that name."
            )
    elif len(kwargs) > 0 and param_name in kwargs:
        print(
            f"WARNING. Parameter {param_name} is not a keyword argument, but the function takes a keyword argument of that name. This may cause unexpected behavior. Consider setting keyword=True for the parameter."
        )

    return errors


def validate_tool_list(tool_list):
    if not isinstance(tool_list, dict):
        raise TypeError("tool_list must be a dictionary.")

    errors = []
    args = (0, [])

    for tool_name in tool_list.keys():
        if len(tool_name) == 0:
            errors.append("Tool names cannot be empty.")
        if len(tool_name) > 50:
            errors.append("Tool names cannot be longer than 50 characters.")

        if not isinstance(tool_list[tool_name], dict):
            errors.append(f"{tool_name} must contain a dictionary.")

        tool = tool_list[tool_name]
        if "description" not in tool:
            errors.append(f"{tool_name} must contain a description.")
        else:
            if not isinstance(tool["description"], str):
                errors.append(f"{tool_name} description must be a string.")
            if len(tool["description"]) > 500:
                errors.append(
                    f"{tool_name} description cannot be longer than 500 characters."
                )
            if len(tool["description"]) == 0:
                errors.append(f"{tool_name} description cannot be empty.")

        if "function" not in tool:
            errors.append(f"{tool_name} must contain a function.")
        else:
            if not callable(tool["function"]):
                errors.append(f"{tool_name} function must be callable.")
            else:
                args = get_args(tool["function"])

        if "parameters" not in tool:
            errors.append(f"{tool_name} must contain parameters.")
        else:
            if not isinstance(tool["parameters"], list):
                errors.append(f"{tool_name} parameters must be a list.")
            else:
                if len(tool["parameters"]) == 0:
                    errors.append(f"{tool_name} parameters cannot be empty.")
                else:
                    for parameter in tool["parameters"]:
                        if not isinstance(parameter, dict):
                            errors.append(
                                f"{tool_name} parameters must be a list of dictionaries."
                            )
                        else:
                            errors += validate_parameter(parameter, args)

        if "function" in tool and callable(tool["function"]):
            if "parameters" in tool and len(tool["parameters"]) > len(
                inspect.signature(tool["function"]).parameters
            ):
                errors.append(
                    f"{tool_name} function must have less or the same number of parameters as the number of taken by the functionparameters."
                )

    if len(errors) > 0:
        for error in errors:
            print(error)
        return False

    return True
