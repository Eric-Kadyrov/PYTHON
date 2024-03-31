def snake_case_to_camel_case(snake_str):
    components = snake_str.split('_')  # Splitting the string by underscores
    # Capitalize the first letter of each component and join them together
    camel_case_str = ''.join(x.title() for x in components)
    return camel_case_str

# Example usage
start_string = "snake_case_text"
end_string = snake_case_to_camel_case(start_string)
print(f"Converted string: {end_string}")