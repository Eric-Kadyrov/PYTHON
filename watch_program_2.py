import tkinter as tk
import time

class ClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CLOCK")
        
        self.running = False
        self.paused = False
        
        # Time label to display time with dark blue background
        self.time_label = tk.Label(root, font=("Arial", 40), bg="dark blue", fg="white")
        self.time_label.pack(pady=20)
        
        # Control buttons with specified colors
        self.go_button = tk.Button(root, text="Go", command=self.start_clock, width=10, bg="green", fg="white")
        self.go_button.pack(side="left", padx=20)
        
        self.pause_button = tk.Button(root, text="Pause", command=self.pause_clock, width=10, bg="yellow", fg="black")
        self.pause_button.pack(side="left", padx=20)
        
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_clock, width=10, bg="red", fg="white")
        self.stop_button.pack(side="left", padx=20)
        
        self.update_clock()

    def update_clock(self):
        if self.running and not self.paused:
            current_time = time.strftime('%H:%M:%S') + '.' + str(int(time.time() * 100) % 100).zfill(2)
            self.time_label.config(text=current_time)
        
        self.root.after(10, self.update_clock)
    
    def start_clock(self):
        self.running = True
        self.paused = False

    def pause_clock(self):
        if self.running:
            self.paused = not self.paused

    def stop_clock(self):
        self.running = False
        self.time_label.config(text="00:00:00.00")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClockApp(root)
    root.mainloop()