def get_value_by_key_sequence(json, keys):
    curr_json = json

    for key in keys:
        curr_json = \
            [get_value_by_key_sequence(value, [key]) for value in curr_json if get_value_by_key_sequence(value, [key])][0] \
            if isinstance(curr_json, list) else curr_json.get(key)

    return curr_json
