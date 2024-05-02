import random
import string

def create_files_and_summary():
    summary_data = []
    
    # Generate files A.txt to Z.txt
    for letter in string.ascii_uppercase:
        file_name = f"{letter}.txt"
        number = random.randint(1, 100)
        
        # Write the random number to the respective file
        with open(file_name, "w") as file:
            file.write(str(number))
        
        # Append file name and number to summary list
        summary_data.append(f"{file_name}: {number}")
    
    # Write summary file
    with open("summary.txt", "w") as summary_file:
        summary_file.write("\n".join(summary_data))

# Call the function to execute the task
create_files_and_summary()