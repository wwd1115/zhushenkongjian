def circuit_points(x1, y1, x2, y2, y_bias=True):
    # Returns 4 points for an orthogonal line
    if y_bias:
        mid_y = (y1 + y2) / 2
        return [x1, y1, x1, mid_y, x2, mid_y, x2, y2]
    else:
        mid_x = (x1 + x2) / 2
        return [x1, y1, mid_x, y1, mid_x, y2, x2, y2]

print(circuit_points(0, 0, 100, 100))
