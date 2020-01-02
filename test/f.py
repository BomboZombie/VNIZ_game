def f1(x0, y0, delta_y):
    for y in range(min(y0, y0 + delta_y), max(y0, y0 + delta_y)):
        yield (x0, y)


def f2(x0, y0, delta_y):
    # return [x0] * abs(delta_y)
    # return range(min(y0, y0 + delta_y), max(y0, y0 + delta_y))
    return zip([x0] * abs(delta_y),
               range(min(y0, y0 + delta_y), max(y0, y0 + delta_y)))


print(list(f1(228, 4, 10)))
print(list(f2(228, 4, 10)))