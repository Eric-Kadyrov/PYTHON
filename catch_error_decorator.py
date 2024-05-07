def catch_errors(func):
    def wrapper(*args, **kwargs):
        try:
            # Execute the original function
            return func(*args, **kwargs)
        except Exception as e:
            # Catch any exception, print an error message and handle the error
            print(f"Found 1 error during execution of your function: {type(e).__name__} {str(e)}")
            # Optionally, you could also re-raise the exception if you want it to propagate:
            # raise
    return wrapper

@catch_errors
def some_function_with_risky_operation(data):
    # This function might raise a KeyError if the key 'key' is not present in the dictionary 'data'
    print(data['key'])

# Test the function with missing 'key' in the dictionary
some_function_with_risky_operation({'foo': 'bar'})
# Expected output: Found 1 error during execution of your function: KeyError 'key'

# Test the function with the correct 'key' in the dictionary
some_function_with_risky_operation({'key': 'bar'})
# Expected output: bar