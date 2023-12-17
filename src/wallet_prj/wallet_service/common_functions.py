
# geeting detailed error response
def get_json_errors(error_list_data):
    __field_errors = {}

    field_errors = [(k, v[0]) for k, v in error_list_data.items()]

    for key, error_list in field_errors:
        __field_errors[key] = error_list

    return __field_errors
