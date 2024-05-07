is_admin(func):
    def wrapper(*args, **kwargs):
        # Check if 'user_type' is provided in kwargs and if it is 'admin'
        if kwargs.get('user_type') != 'admin':
            raise ValueError('Permission denied')
        # Call the original function if the user is an admin
        return func(*args, **kwargs)
    return wrapper

@is_admin
def show_customer_receipt(user_type: str):
    # Some very dangerous operation
    print("Receipt: You've accessed sensitive customer data.")

# Test the function with different user types
try:
    show_customer_receipt(user_type='user')
except ValueError as e:
    print(e)  # This will print "Permission denied" because user_type is 'user'
