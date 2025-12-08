def print_data_structure(data, indent=0):
    """Recursively prints only the keys of a nested dictionary."""
    if not isinstance(data, dict) and not isinstance(data, list):
        print("  " * indent + str(type(data)))
    elif isinstance(data, dict):
        for key, value in data.items():
            print("  " * indent + str(key))
            print_data_structure(value, indent + 1)
    else:
        print("  " * (indent + 1) + f"[list]")
        if len(data) > 0:
            print_data_structure(data[0], indent + 2)