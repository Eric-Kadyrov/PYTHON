def triangle_area(x1, y1, x2, y2, x3, y3):
    area = abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2.0
    return area

# Example usage
x1, y1 = 0, 0  # Coordinates of the first vertex
x2, y2 = 4, 0  # Coordinates of the second vertex
x3, y3 = 0, 3  # Coordinates of the third vertex

# Calculate the area
area = triangle_area(x1, y1, x2, y2, x3, y3)
print(f"The area of the triangle is: {area}")