def crate_number_list(start, end):
    if start is None:
        start = 1
    if end is None:
        return [start]
    arr = []
    i = start
    while i <= end:
        arr.append(i)
        i = i + 1
    return arr
