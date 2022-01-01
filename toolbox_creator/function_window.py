import threading
import datetime
import PySimpleGUIQt as sg
from PySimpleGUIQt.PySimpleGUIQt import (
    BUTTON_TYPE_BROWSE_FILE,
    BUTTON_TYPE_BROWSE_FILES,
    BUTTON_TYPE_SAVEAS_FILE,
    BUTTON_TYPE_BROWSE_FOLDER,
    POPUP_BUTTONS_NO_BUTTONS,
    WIN_CLOSED,
)
from toolbox_creator.globe_icon import globe_icon
from toolbox_creator.date_picker import popup_get_date
from toolbox_creator.function_validation import (
    validate_inputs,
    update_inputs,
)
from toolbox_creator.utils import (
    get_default_date,
    get_first_key,
    parse_date,
    get_today_date,
    default_texts,
)


def create_layout(name, tools, create_console=False, scalar=1.0):
    if name not in tools:
        raise Exception("Tool not found")

    layout = []
    listeners = []

    radio_group_id = 1
    for parameter in tools[name]["parameters"]:
        parameter_name = list(parameter.keys())[0]
        parameter_type = parameter[parameter_name]["type"]

        if "default" in parameter[parameter_name]:
            default = parameter[parameter_name]["default"]
        else:
            default = False

        if "tooltip" in parameter[parameter_name]:
            tooltip = parameter[parameter_name]["tooltip"]
        else:
            tooltip = None

        if "default_extension" in parameter[parameter_name]:
            default_extension = parameter[parameter_name]["default_extension"]
        else:
            default_extension = [("*", "All Files")]

        if "default_date" in parameter[parameter_name]:
            default_date = parse_date(parameter[parameter_name]["default_date"])
        else:
            default_date = get_today_date()

        if "display_name" in parameter[parameter_name]:
            display_name = parameter[parameter_name]["display_name"]
        else:
            display_name = parameter_name

        if "enabled_by" in parameter[parameter_name]:
            enabled_by = True
            enabled_by_key = get_first_key(parameter[parameter_name]["enabled_by"])
            enabled_by_val = parameter[parameter_name]["enabled_by"][enabled_by_key]
            listeners.append(
                {
                    "parameter": parameter_name,
                    "enabled_by": enabled_by_key,
                    "values": enabled_by_val,
                }
            )
        else:
            enabled_by = False

        default_date_str = datetime.datetime(
            default_date[2], default_date[0], default_date[1]
        ).strftime("%Y%m%d")

        text_height = scalar * 1.2
        input_pad = ((0, round(10 * scalar)), (0, 0))
        button_size = (round(16 * scalar), text_height)
        input_size = (round(54 * scalar), text_height)
        text_size = (round(24 * scalar), text_height)
        param_input = None
        path_input = None
        justification = "center"
        if parameter_type == "file_open":
            param_input = sg.Button(
                "Browse",
                button_type=BUTTON_TYPE_BROWSE_FILE,
                key=parameter_name + "_picker",
                border_width=0,
                enable_events=True,
                size=button_size,
                tooltip=tooltip,
                target=parameter_name,
            )
            path_input = sg.In(
                default_text=default_texts[0],
                key=parameter_name,
                justification=justification,
                enable_events=True,
                disabled=False,
                tooltip=tooltip,
                size=(input_size[0] - button_size[0] - 1, input_size[1]),
                pad=input_pad,
            )
        elif parameter_type == "file_open_multiple":
            param_input = sg.Button(
                "Browse",
                button_type=BUTTON_TYPE_BROWSE_FILES,
                key=parameter_name + "_picker",
                enable_events=True,
                border_width=0,
                size=button_size,
                tooltip=tooltip,
                target=parameter_name,
            )
            path_input = sg.In(
                default_text=default_texts[1],
                key=parameter_name,
                enable_events=True,
                disabled=False,
                tooltip=tooltip,
                justification=justification,
                size=(input_size[0] - button_size[0] - 1, input_size[1]),
                pad=input_pad,
            )
        elif parameter_type == "file_save":
            param_input = sg.Button(
                "Save As",
                button_type=BUTTON_TYPE_SAVEAS_FILE,
                border_width=0,
                key=parameter_name + "_picker",
                enable_events=True,
                size=button_size,
                tooltip=tooltip,
                target=parameter_name,
                file_types=default_extension,
            )
            path_input = sg.In(
                default_text=default_texts[2],
                key=parameter_name,
                enable_events=True,
                disabled=False,
                tooltip=tooltip,
                justification=justification,
                size=(input_size[0] - button_size[0] - 1, input_size[1]),
                pad=input_pad,
            )
        elif parameter_type == "folder_save" or parameter_type == "folder_open":
            param_input = sg.Button(
                "Browse",
                button_type=BUTTON_TYPE_BROWSE_FOLDER,
                border_width=0,
                key=parameter_name + "_picker",
                enable_events=True,
                size=button_size,
                tooltip=tooltip,
                target=parameter_name,
            )
            path_input = sg.In(
                default_text=default_texts[3],
                key=parameter_name,
                enable_events=True,
                disabled=False,
                tooltip=tooltip,
                justification=justification,
                size=(input_size[0] - button_size[0] - 1, input_size[1]),
                pad=input_pad,
            )
        elif (
            parameter_type == "number"
            or parameter_type == "string"
            or parameter_type == "password"
        ):
            param_input = sg.InputText(
                key=parameter_name,
                enable_events=True,
                password_char="*" if parameter_type == "password" else "",
                default_text=default,
                tooltip=tooltip,
                background_color="#f1f1f1",
                size=input_size,
                pad=input_pad,
            )
        elif parameter_type == "boolean":
            param_input = sg.Checkbox(
                "",
                key=parameter_name,
                enable_events=True,
                default=default,
                tooltip=tooltip,
                pad=((0, 0), (round(8 * scalar), 0)),
            )
        elif parameter_type == "slider":
            param_args = parameter[parameter_name].keys()
            min_value = (
                parameter[parameter_name]["min_value"]
                if "min_value" in param_args
                else 0
            )
            max_value = (
                parameter[parameter_name]["max_value"]
                if "max_value" in param_args
                else 100
            )
            default_value = (
                parameter[parameter_name]["default"] if "default" in param_args else 50
            )
            step = parameter[parameter_name]["step"] if "step" in param_args else 1

            if default < min_value or default > max_value:
                default = min_value

            param_input = sg.Slider(
                range=(min_value, max_value),
                orientation="h",
                default_value=default_value,
                enable_events=True,
                tick_interval=step,
                key="slider_" + parameter_name,
                tooltip=tooltip,
                size_px=(round(360 * scalar), round(38 * scalar)),
                pad=input_pad,
            )

            path_input = sg.In(
                default_text=default,
                key=parameter_name,
                enable_events=True,
                disabled=False,
                tooltip=tooltip,
                size=button_size,
                pad=input_pad,
                justification=justification,
            )
        elif parameter_type == "dropdown":
            param_options = parameter[parameter_name]["options"]

            labels = []
            selected = None
            for idx, option in enumerate(param_options):
                labels.append(option["label"])
                if "default" in option.keys() and option["default"] == True:
                    selected = option["label"]

            param_input = sg.Combo(
                labels,
                default_value=selected,
                key=parameter_name,
                metadata=option["value"],
                background_color="#f1f1f1",
                readonly=True,
                enable_events=True,
                visible_items=10,
                tooltip=tooltip,
                size=(input_size[0] - button_size[0] - 1, input_size[1]),
            )
        elif parameter_type == "radio":
            param_options = parameter[parameter_name]["options"]
            param_input = []
            for idx, option in enumerate(param_options):
                if "default" in option.keys() and option["default"] == True:
                    selected = True
                else:
                    selected = False

                left_pad = 0 if idx == 0 else round(16 * scalar)

                param_input.append(
                    sg.Radio(
                        option["label"],
                        radio_group_id,
                        default=selected,
                        key=parameter_name + "_" + option["key"],
                        metadata=option["value"],
                        tooltip=tooltip,
                        pad=((left_pad, 0), (0, 0)),
                    )
                )
            radio_group_id += 1
        elif parameter_type == "date_year":
            param_input = sg.Button(
                "Date",
                key="date_picker_" + parameter_name,
                button_type=sg.BUTTON_TYPE_READ_FORM,
                enable_events=True,
                tooltip=tooltip,
                bind_return_key=True,
                border_width=0,
                size=button_size,
            )
            path_input = sg.Input(
                default_date_str,
                key=parameter_name,
                enable_events=True,
                tooltip=tooltip,
                visible=True,
                disabled=False,
                justification=justification,
                size=(input_size[0] - button_size[0] - 1, input_size[1]),
                pad=input_pad,
            )

        if param_input is not None:
            param_text = sg.Text(
                display_name,
                tooltip=tooltip,
                key=parameter_name + "_text",
                background_color=sg.theme_background_color(),
                size=text_size,
                pad=((0, 0), (0, 0)),
                margins=(0, 0, round(4 * scalar), 0),
                justification="right",
            )

            if not isinstance(param_input, list):
                param_inputs = [param_input]
            else:
                param_inputs = param_input

            if parameter_type != "radio" and path_input is not None:
                if parameter_type in [
                    "date_year",
                    "file_open",
                    "file_open_multiple",
                    "folder_save",
                    "folder_open",
                    "file_save",
                    "slider",
                ]:
                    param_inputs = [path_input, param_input]
                else:
                    param_inputs = [param_input, path_input]

            show_row = True
            if enabled_by:
                found = False
                found_val = None
                for param in tools[name]["parameters"]:
                    if get_first_key(param) == enabled_by_key:
                        found_keys = param[enabled_by_key]

                        if "default" not in found_keys and "options" not in found_keys:
                            raise Exception(
                                f"No default value for {get_first_key(param)} required by 'enabled_by' on {parameter_name}"
                            )

                        if "options" in found_keys and "default" not in found_keys:
                            found_default = False
                            for option in found_keys["options"]:
                                if "default" in option and option["default"] is True:
                                    found_val = option["value"]
                                    found_default = True

                            if found_default is False:
                                raise Exception(
                                    f"No default value for {get_first_key(param)} required by 'enabled_by' on {parameter_name}"
                                )
                        else:
                            found_val = found_keys["default"]

                        found = True
                        break

                if found is False:
                    raise Exception(
                        f"No parameter found for 'enabled_by' on {parameter_name}. Searched for: {enabled_by_key}"
                    )

                if found_val not in enabled_by_val:
                    show_row = False

            append = [
                sg.Column(
                    [
                        [param_text],
                    ],
                    size=(round(120 * scalar), round(36 * scalar)),
                    pad=((0, 0), (0, 0)),
                    element_justification="r",
                    visible=show_row,
                    key=parameter_name + "_col1",
                ),
                sg.Column(
                    [
                        param_inputs,
                    ],
                    size=(round(260 * scalar), round(36 * scalar)),
                    pad=((0, 0), (0, 0)),
                    visible=show_row,
                    key=parameter_name + "_col2",
                ),
            ]

            layout.append(append)

    layout.append(
        [
            sg.Column(
                [
                    [
                        sg.Text("", size=(round(26 * scalar), button_size[1])),
                        sg.Button(
                            "Run",
                            size=button_size,
                            key="-RUN-BUTTON-",
                            visible=True,
                            border_width=0,
                        ),
                        sg.Text("", size=(1, button_size[1])),
                        sg.Button(
                            "Exit",
                            size=button_size,
                            button_color=(sg.theme_background_color(), "#B22222"),
                            key="-EXIT-BUTTON-",
                            border_width=0,
                        ),
                    ]
                ],
            )
        ]
    )

    layout.append(
        [
            sg.Text("", size=(round(36 * scalar), None)),
            sg.Text(
                "Progress:",
                key="-PROGRESS-TEXT-",
                pad=((round(20 * scalar), round(100 * scalar)), (0, 0)),
            ),
            sg.Column(
                [
                    [
                        sg.ProgressBar(
                            1,
                            orientation="h",
                            key="-PROGRESS-",
                            pad=((0, round(24 * scalar)), (0, 0)),
                            size=(
                                input_size[0] - round(4 * scalar),
                                round(36 * scalar),
                            ),
                        ),
                        sg.Button(
                            "Cancel",
                            key="-CANCEL-BUTTON-",
                            button_color=(sg.theme_background_color(), "#d7a824"),
                            border_width=0,
                            size=button_size,
                            pad=((round(10 * scalar), 0), (0, 0)),
                        ),
                    ],
                ],
                pad=((round(10 * scalar), round(10 * scalar)), (0, 0)),
                size=(round(520 * scalar), round(36 * scalar)),
            ),
        ]
    )

    if create_console:
        layout.append(
            [
                sg.Output(
                    pad=((0, 0), (round(10 * scalar), round(10 * scalar))),
                    size_px=(None, round(200 * scalar)),
                    background_color="#f1f1f1",
                ),
            ]
        )

    layout = [
        [
            sg.Column(
                layout,
                size=(round(900 * scalar), None),
                scrollable=True,
                element_justification="left",
                pad=((0, 0), (0, 0)),
            ),
            sg.Button("-THREAD-", visible=False),
        ]
    ]

    return (layout, tools[name]["function"], listeners)


def create_function_window(
    function_name,
    tools,
    create_console=False,
    icon=globe_icon,
    theme="Reddit",
    scalar=1.0,
):
    sg.theme(theme)

    sg.set_options(
        element_padding=(0, 0),
        margins=(0, 0),
        font=("Helvetica", 10),
        border_width=0,
    )

    layout, buteo_function, listeners = create_layout(
        function_name, tools, create_console=create_console, scalar=scalar
    )

    window_func = sg.Window(
        function_name,
        layout,
        resizable=True,
        size=(int(900 * scalar), int(1100 * scalar)),
        finalize=True,
        icon=icon,
        element_justification="center",
        border_depth=0,
        element_padding=(0, 0),
    )

    progress_bar = window_func["-PROGRESS-"]
    progress_bar.UpdateBar(0, 100)
    print("Opening function:", function_name)

    thread = None
    run_clicked = False
    while True:
        event_func, values_func = window_func.read()

        if (
            event_func == "-EXIT-BUTTON-"
            or event_func == WIN_CLOSED
            or event_func is None
        ):
            break
        elif event_func == "-RUN-BUTTON-":
            run_clicked = True

            try:
                validation = validate_inputs(
                    function_name, values_func, window_func, tools
                )

                if False in validation["valid"]:
                    sg.popup(
                        "\n".join(validation["message"]),
                        title="Error",
                        keep_on_top=True,
                        no_titlebar=False,
                        grab_anywhere=True,
                        button_type=POPUP_BUTTONS_NO_BUTTONS,
                        non_blocking=True,
                    )
                    progress_bar.UpdateBar(0, 100)
                else:
                    args = validation["cast_args"]
                    kwargs = validation["cast_kwargs"]

                    def long_operation_thread(window):
                        global thread_message

                        buteo_return = None
                        try:
                            buteo_return = buteo_function(*args, **kwargs)
                            thread_message = buteo_return
                        except Exception as e:
                            thread_message = ("Error", e)
                        window["-THREAD-"].click()

                        return buteo_return

                    progress_bar.UpdateBar(10, 100)
                    window_func["-PROGRESS-TEXT-"].update("Running..")
                    window_func["-RUN-BUTTON-"].update(
                        button_color=(sg.theme_element_text_color(), "#999999")
                    )

                    thread = threading.Thread(
                        target=long_operation_thread,
                        args=(window_func,),
                        daemon=True,
                    )
                    thread.start()

            except Exception as e:
                progress_bar.UpdateBar(0, 100)
                window_func["-PROGRESS-TEXT-"].update("Progress:")
                window_func["-RUN-BUTTON-"].update(button_color=sg.theme_button_color())

                sg.Popup("Error", str(e))

        elif event_func == "-THREAD-":
            try:
                thread.join(timeout=0)
                print(thread_message)
            except:
                print("Error joining thread")

            if isinstance(thread_message, list) and thread_message[0] == "Error":
                sg.Popup("Error", str(thread_message[1]))
                window_func["-PROGRESS-TEXT-"].update("Progress:")
                progress_bar.UpdateBar(0, 100)
            else:
                window_func["-PROGRESS-TEXT-"].update("Completed.")
                progress_bar.UpdateBar(100, 100)

            window_func["-RUN-BUTTON-"].update(button_color=sg.theme_button_color())
        elif (
            isinstance(event_func, str)
            and len(event_func) > 12
            and event_func[:12] == "date_picker_"
        ):
            target_param = event_func[12:]
            try:
                default_date = get_default_date(target_param, window_func)
                date = popup_get_date(
                    icon=globe_icon,
                    start_year=default_date[0],
                    start_mon=default_date[1],
                    start_day=default_date[2],
                )

                if date is not None:
                    window_func[event_func[12:]].update(value=date)
                    if run_clicked:
                        validate_inputs(function_name, values_func, window_func, tools)
            except Exception as e:
                sg.Popup("Error", str(e))

        elif (
            isinstance(event_func, str)
            and len(event_func) > len("slider_")
            and event_func[: len("slider_")] == "slider_"
        ):
            target_param = event_func[len("slider_") :]
            window_func[target_param].update(value=values_func[event_func])
            if run_clicked:
                validate_inputs(function_name, values_func, window_func, tools)
        else:
            update_inputs(
                event_func,
                values_func,
                window_func,
                listeners,
                function_name,
                tools,
            )
            if run_clicked:
                validate_inputs(function_name, values_func, window_func, tools)

    window_func.close()
