import os
import PySimpleGUIQt as sg
from multiprocessing import Process, freeze_support
from toolbox_creator.globe_icon import globe_icon
from toolbox_creator.base import home_layout
from toolbox_creator.form import open_function
from toolbox_creator.funcs import (
    get_list_of_functions,
    get_function_description,
    validate_tool_list,
)


KEY_UP_QT = "special 16777235"
KEY_DOWN_QT = "special 16777237"
KEY_ENTER_QT = "special 16777220"
DEFAULT_MARGINS = (0, 0)
DEFAULT_ELEMENT_PADDING = (0, 0)
DEFAULT_FONT = ("Helvetica", 10)
DEFAULT_TEXT_JUSTIFICATION = "left"
DEFAULT_BORDER_WIDTH = 0


def select_function(function_name, window, tools):
    description = get_function_description(function_name, tools)
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
    if not validate_tool_list(tools_list):
        print("Unable to create GUI due to invalid setup list.")
        return

    if auto_scale:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    sg.theme(theme)

    if icon is False:
        icon = globe_icon

    available_functions = get_list_of_functions(tools_list)

    window = sg.Window(
        name,
        home_layout(
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

                freeze_support()

                p = Process(
                    target=open_function,
                    args=(
                        function_name,
                        tools_list,
                        create_console,
                        icon,
                        theme,
                        scalar,
                    ),
                )
                p.start()
                open_windows.append(p)
                # open_function(
                #     function_name,
                #     tools_list,
                #     create_console=create_console,
                #     icon=icon,
                #     scalar=scalar,
                # )
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


# pyinstaller -wF --noconfirm --clean --noconsole --icon=./gui_elements/globe_icon.ico gui.py
