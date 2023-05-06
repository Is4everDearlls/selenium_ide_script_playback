from typing import Dict, List, Union

import jsonpath


def json_data_extract(data: Union[Dict, List], expression: str):
    data = jsonpath.jsonpath(data, expression)
    return data[0] if data and len(data) == 1 else data
