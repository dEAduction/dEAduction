

def inj_list(list_: list):
    """
    Return a list with same elements of list_ but no repetition.
    """
    new_list = []
    for item in list_:
        if item not in new_list:
            new_list.append(item)
    return new_list


def injective_union(list_of_lists):
    """
    Return the injective union of list of lists.
    """
    if len(list_of_lists) == 1:
        return list_of_lists[0]

    else:
        return inj_list(list_of_lists[0] + injective_union(list_of_lists[1:]))


def intersection_list(list_of_lists):
    """
    Return the list of elements that are in all lists of iter, an iterable of
    lists.
    """
    if len(list_of_lists) == 1:
        return list_of_lists[0]

    elif len(list_of_lists) == 2:
        list0 = list_of_lists[0]
        list1 = list_of_lists[1]
        return [item for item in list0 if item in list1]

    else:
        return intersection_list([list_of_lists[0],
                                 intersection_list(list_of_lists[1:])])


