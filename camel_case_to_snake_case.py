import re

def camel_case_to_snake_case(camel_str):
    # Inserting an underscore between lowercase and uppercase letters
    snake_str = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', camel_str)
    return snake_str.lower()  # Converting the whole string to lowercase

# Example usage
start_string = "SnakeCaseText"
end_string = camel_case_to_snake_case(start_string)
print(f"Converted string: {end_string}")