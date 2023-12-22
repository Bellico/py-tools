input = [
    ["jen", "facebook", "1312"],
    ["jen", "facebook", "1211"],
    ["jen", "facebook", "1213"],
    ["jen", "facebook", "1311"],
    ["jen", "facebook", "1998"],
    ["jen", "facebook", "121198"],
    ["jen", "facebook", "131198"],
    ["facebook", "jen", "1312"],
    ["facebook", "jen", "1211"],
    ["facebook", "jen", "1213"],
    ["facebook", "jen", "1311"],
    ["facebook", "jen", "1998"],
    ["facebook", "jen", "121198"],
    ["facebook", "jen", "131198"],
    ["jennny", "facebook", "1312"],
    ["jennny", "facebook", "1211"],
    ["jennny", "facebook", "1213"],
    ["jennny", "facebook", "1311"],
    ["jennny", "facebook", "1998"],
    ["facebook", "jenny", "1312"],
    ["facebook", "jenny", "1211"],
    ["facebook", "jenny", "1213"],
    ["facebook", "jenny", "1311"],
    ["facebook", "jenny", "1998"],
    ["facebook", "jenny", "121198"],
    ["facebook", "jenny", "131198"],
    ["princia", "jen", "1312"],
    ["princia", "jen", "1211"],
    ["princia", "jen", "1213"],
    ["princia", "jen", "1311"],
    ["princia", "jen", "1998"],
    ["princia", "jen", "121198"],
    ["princia", "jen", "131198"],
    ["princia", "jen", "facebook", "1312"],
    ["princia", "jen", "facebook", "1211"],
    ["princia", "jen", "facebook", "1213"],
    ["princia", "jen", "facebook", "1311"],
    ["princia", "jen", "facebook", "1998"],
    ["princia", "jen", "facebook", "121198"],
    ["princia", "jen", "facebook", "131198"],
    ["facebook", "princia", "jen", "1312"],
    ["facebook", "princia", "jen", "1211"],
    ["facebook", "princia", "jen", "1213"],
    ["facebook", "princia", "jen", "1311"],
    ["facebook", "princia", "jen", "1998"],
    ["facebook", "princia", "jen", "121198"],
    ["facebook", "princia", "jen", "131198"],
    ["fb", "princia", "jen", "1312"],
    ["fb", "princia", "jen", "1211"],
    ["fb", "princia", "jen", "1213"],
    ["fb", "princia", "jen", "1311"],
    ["fb", "princia", "jen", "1998"],
    ["fb", "princia", "jen", "121198"],
    ["fb", "princia", "jen", "131198"]
]

output = []


def concat_simple(elements):
    result = ""
    for i, n in enumerate(elements):
        result += elements[i]
    return result


def concat_with_dot(elements):
    result = ""
    for i, n in enumerate(elements):
        result += elements[i]
        if i < len(elements) - 1:
            result += "."
    return result


def concat_with_dot_on_first(elements):
    result = ""
    for i, n in enumerate(elements):
        result += elements[i]
        if i == 0:
            result += "."
    return result


def concat_with_dot_on_last(elements):
    result = ""
    for i, n in enumerate(elements):
        result += elements[i]
        if i == len(elements) - 2:
            result += "."
    return result


def capitalize_every(elements):
    copy = elements.copy()
    for i, n in enumerate(copy):
        copy[i] = copy[i].capitalize()
    return copy


def capitalize_first(elements):
    copy = elements.copy()
    copy[0] = copy[0].capitalize()
    return copy


def capitalize_second(elements):
    copy = elements.copy()
    copy[1] = copy[1].capitalize()
    return copy


def capitalize_last(elements):
    copy = elements.copy()
    i = len(copy) - 1
    copy[i] = copy[i].capitalize()
    return copy


def upper_first(elements):
    copy = elements.copy()
    copy[0] = copy[0].upper()
    return copy


def insert_1(elements):
    copy = elements.copy()
    copy.insert(0, "1")
    return copy


def do_concat(elements):
    output.append(concat_simple(elements))
    output.append(concat_with_dot(elements))
    output.append(concat_with_dot_on_first(elements))
    output.append(concat_with_dot_on_last(elements))


def do_stuff(elements):
    do_concat(elements)
    do_concat(capitalize_every(elements))
    do_concat(capitalize_first(elements))
    do_concat(capitalize_second(elements))
    do_concat(capitalize_last(elements))
    do_concat(upper_first(elements))

    do_concat(insert_1(elements))
    do_concat(insert_1(capitalize_every(elements)))
    do_concat(insert_1(capitalize_first(elements)))
    do_concat(insert_1(capitalize_second(elements)))
    do_concat(insert_1(capitalize_last(elements)))
    do_concat(insert_1(upper_first(elements)))


for i in input:
    do_stuff(i)

with open('full.txt', 'w') as f:
    for line in output:
        f.write(f"{line}\n")

print(len(output))
