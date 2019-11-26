def validate_required_kwargs_are_not_empty(args_list, kwargs):
    """
    This function checks whether all passed keyword arguments are present and that they have truthy values.
    ::args::
    args_list - This is a list or tuple that contains all the arguments you want to query for. The arguments are strings seperated by comma.
    kwargs - A dictionary of keyword arguments you where you want to ascertain that all the keys are present and they have truthy values.
    """

    for arg in args_list:
        if arg not in kwargs.keys():
            raise TypeError(f"{arg} must be provided.")
        if not kwargs.get(arg):
            raise TypeError(f"{arg} cannot be empty.")
    return kwargs
