def get_named_entities(data):
    rowarray_list = []

    for row in data:
        dictionary_entity = dict(zip(row.keys(), row))
        rowarray_list.append(dictionary_entity)
    
    return rowarray_list
    
