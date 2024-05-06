# Content to be written in the first file
content = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

# Write the content to the first file
with open("LoremIpsum.txt", "w") as file:
    file.write(content)

# Read from the first file, convert to uppercase, and write to the second file
with open("LoremIpsum.txt", "r") as file:
    content_upper = file.read().upper()

with open("LoremIpsumUpperCase.txt", "w") as file:
    file.write(content_upper)