def is_palindrome():
    return s == s[::-1]
user_input = input("Enter a string:")
result = is_palindrome(user_input)
print(f"Is {user_input} a palindrome? {result}")