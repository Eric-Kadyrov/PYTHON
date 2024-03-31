import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup

# Function to scrape the headlines
def scrape_headlines():
    # Clear the output area
    output_text.delete('1.0', tk.END)
    
    # Get the URL from the input field
    url = url_entry.get()
    
    # Fetch the content from the URL
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Assuming headlines are stored in <h3> tags; adjust as needed
        headlines = soup.find_all('h2')
        
        # Display each headline in the output area
        for headline in headlines:
            output_text.insert(tk.END, headline.text.strip() + '\n')
    except Exception as e:
        output_text.insert(tk.END, f"Error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Web Scraping App")

# Create and pack the widgets
url_label = tk.Label(root, text="Enter URL:")
url_label.pack()

url_entry = tk.Entry(root, width=50)
url_entry.pack()

scrape_button = tk.Button(root, text="Scrape Headlines", command=scrape_headlines)
scrape_button.pack()

output_label = tk.Label(root, text="Headlines:")
output_label.pack()

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
output_text.pack()

# Start the GUI event loop
root.mainloop()