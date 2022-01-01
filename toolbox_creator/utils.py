import inspect
import datetime


def get_args(func):
    args = 0
    kwargs = []
    params = inspect.signature(func).parameters
    for param_name in params:
        param = params[param_name]
        if param.default == inspect.Parameter.empty:
            args += 1
        else:
            kwargs.append(param.name)

    return args, kwargs


def get_list_of_keys(tools):
    return [i for i in tools.keys()]


def get_first_key(dictionary):
    for key in dictionary.keys():
        return key


def add_slash_to_end(path):
    if path[-1] != "/":
        path += "/"
    return path


def get_today_date():
    today = datetime.date.today()
    return (today.month, today.day, today.year)


def get_days_ago(days_ago):
    today = datetime.date.today()
    delta = datetime.timedelta(days_ago)

    fortnight = today - delta
    return (fortnight.month, fortnight.day, fortnight.year)


def parse_date(date_str):
    if date_str == "today":
        return get_today_date()

    elif "days_ago" in date_str:
        days = round(date_str.split("_")[2])
        return get_days_ago(days)
    else:
        return get_today_date()


def get_param_name(tool_params):
    for key in tool_params.keys():
        return key


def get_default_date(target_param, window):
    date_str = window[target_param].Get()

    return (round(date_str[0:4]), round(date_str[4:6]), round(date_str[6:8]))


default_texts = [
    "Choose a file..",
    "Choose files..",
    "Target file..",
    "Target folder..",
]
