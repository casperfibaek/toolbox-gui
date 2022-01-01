import os
import PySimpleGUIQt as sg
from multiprocessing import Process
from toolbox_creator.globe_icon import globe_icon
from toolbox_creator.function_window import create_function_window
from toolbox_creator.function_validation import validate_tool_list
from toolbox_creator.utils import get_list_of_keys

global window_opened
window_opened = False


def tool_selector_layout(functions, scalar=1.0, top_menu=True):
    """Creates the layout for the tool selector."""
    description = "Select a function to run."

    menu_def = [
        ["&File", ["E&xit"]],
        [
            "&Options",
            ["Paths", "Defaults"],
        ],
        [
            "&Help",
            ["Documentation", "About"],
        ],
    ]

    col1 = sg.Column(
        [
            [
                sg.Listbox(
                    [str(i) for i in functions],
                    key="-FUNC-LIST-",
                    size_px=(round(300 * scalar), None),
                    pad=((0, 0), (0, 0)),
                    enable_events=True,
                    default_values=[functions[0]],
                )
            ]
        ],
        size=(round(300 * scalar), None),
        pad=((0, 0), (0, 0)),
    )

    col2 = sg.Column(
        [
            [
                sg.Multiline(
                    description,
                    size_px=(None, None),
                    key="-DESC-",
                    disabled=True,
                    background_color="#f1f1f1",
                    pad=((0, 0), (0, 0)),
                )
            ],
            [
                sg.Button(
                    "Open Function",
                    key="-BUTTON1-",
                    size_px=(round(500 * scalar), 60),
                    pad=((0, 0), (10, 0)),
                    bind_return_key=True,
                    border_width=0,
                )
            ],
        ],
        size=(round(500 * scalar), None),
        element_justification="left",
        pad=((0, 0), (0, 0)),
    )

    base_layout = [
        sg.Column(
            [[col1, col2]],
            size=(round(920 * scalar), None),
            pad=((0, 0), (0, 0)),
            scrollable=True,
            element_justification="left",
        )
    ]

    if top_menu:
        return [
            [
                sg.Menu(
                    menu_def,
                    tearoff=False,
                )
            ],
            base_layout,
        ]

    return [base_layout]


def select_function(function_name, window, tools):
    """Prints the description of the selected function."""
    description = tools[function_name]["description"]
    window["-DESC-"].update(value=description)


def create_gui(
    tools_list,
    name="toolbox",
    theme="Reddit",
    create_console=False,
    icon=False,
    auto_scale=True,
    scalar=0.6,
    top_menu=False,
):
    """Creates a GUI for the toolbox from a list of tools."""
    global window_opened

    if window_opened:
        return

    if not validate_tool_list(tools_list):
        print("Unable to create GUI due to invalid setup list.")
        return

    if auto_scale:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    sg.theme(theme)

    KEY_UP_QT = "special 16777235"
    KEY_DOWN_QT = "special 16777237"
    KEY_ENTER_QT = "special 16777220"

    sg.set_options(
        element_padding=(0, 0),
        margins=(0, 0),
        font=("Helvetica", 10),
        border_width=0,
    )

    if icon is False:
        icon = globe_icon

    available_functions = get_list_of_keys(tools_list)

    window = sg.Window(
        name,
        tool_selector_layout(
            available_functions,
            scalar=scalar,
            top_menu=top_menu,
        ),
        resizable=True,
        auto_size_buttons=True,
        size=(round(800 * scalar), round(600 * scalar)),
        finalize=True,
        icon=globe_icon,
        element_justification="center",
        return_keyboard_events=True,
        border_depth=0,
    )

    window_opened = True

    select_function(available_functions[0], window, tools_list)
    current_selection = 0
    max_selection = len(available_functions) - 1

    list_not_clicked = True
    ignore_list_update = False
    open_windows = []
    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED or event is None:
            break
        elif (
            event == "-BUTTON1-"
            or event == "-FUNC-LIST-DOUBLE-CLICK-"
            or event == KEY_ENTER_QT
        ):
            if (
                isinstance(values["-FUNC-LIST-"], list)
                and len(values["-FUNC-LIST-"]) != 0
            ):
                function_name = values["-FUNC-LIST-"][0]

                p = Process(
                    target=create_function_window,
                    args=(
                        function_name,
                        tools_list,
                        create_console,
                        icon,
                        theme,
                        scalar,
                    ),
                    daemon=False,
                )
                p.start()
                open_windows.append(p)
        elif event == "-FUNC-LIST-":
            if ignore_list_update:
                ignore_list_update = False
                continue

            list_not_clicked = False
            current_selection = available_functions.index(values[event][0])
            select_function(available_functions[current_selection], window, tools_list)
        elif event == KEY_DOWN_QT and list_not_clicked:
            if current_selection < max_selection:
                ignore_list_update = True
                current_selection += 1
                select_function(
                    available_functions[current_selection], window, tools_list
                )
                window["-FUNC-LIST-"].update(set_to_index=current_selection)
        elif event == KEY_UP_QT and list_not_clicked:
            if current_selection > 0:
                ignore_list_update = True
                current_selection -= 1
                select_function(
                    available_functions[current_selection], window, tools_list
                )
                window["-FUNC-LIST-"].update(set_to_index=current_selection)

    window.close()

    for p in open_windows:
        try:
            p.terminate()
        except Exception:
            pass
