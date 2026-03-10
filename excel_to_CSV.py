import pandas as pd

# Ask user for Excel file name
excel_file = input("Enter Excel file name (example: deals.xlsx): ")

try:
    # Read Excel file
    df = pd.read_excel(excel_file)

    # Create CSV file name
    csv_file = excel_file.replace(".xlsx", ".csv")

    # Save as CSV
    df.to_csv(csv_file, index=False)

    print("\nConversion successful!")
    print("CSV file saved as:", csv_file)

except FileNotFoundError:
    print("Error: File not found.")
except Exception as e:
    print("Error:", e)de