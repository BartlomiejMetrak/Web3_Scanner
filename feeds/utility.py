from collections import abc
import pandas as pd
import time



# Utility functions
def datetime_to_unix_timestamp(dt):
    """
    Convert a datetime object to a UNIX timestamp (seconds since 1970-01-01).
    """
    return int(time.mktime(dt.timetuple()))


def dataframe_from_list(data):
    """
    Create a pandas DataFrame from a nested data structure.

    Parameters:
        data (list): List of nested dictionaries or AttributeDicts.

    Returns:
        DataFrame: Flattened pandas DataFrame.
    """

    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        if isinstance(d, list):
            for i, item in enumerate(d):
                items.extend(flatten_dict(
                    item,
                    f'{parent_key}{sep}{i}' if parent_key else str(i),
                    sep=sep
                ).items())
        elif isinstance(d, abc.Mapping):
            for k, v in d.items():
                new_key = f'{parent_key}{sep}{k}' if parent_key else k
                if isinstance(v, (abc.Mapping, list)):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    # Convert HexBytes or bytes to hex string if necessary
                    if hasattr(v, 'hex'):
                        v = v.hex()
                    items.append((new_key, v))
        else:
            items.append((parent_key, d))
        return dict(items)

    flat_data = [flatten_dict(item) for item in data]
    df = pd.DataFrame(flat_data)
    return df