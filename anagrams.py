def anagrams(s1, s2):
    # Remove spaces and convert to lowercase for a case-insensitive comparison
    s1_cleaned = s1.replace(" ", "").lower()
    s2_cleaned = s2.replace(" ", "").lower()

    # Sort the characters in each string and compare
    return sorted(s1_cleaned) == sorted(s2_cleaned)

# Example usage
s1 = "listen"
s2 = "silent"

# Check if the two strings are anagrams
are_anagrams = anagrams(s1, s2)
print(f"Are '{s1}' and '{s2}' anagrams? {are_anagrams}")