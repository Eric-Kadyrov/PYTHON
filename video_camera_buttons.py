import cv2
import tkinter as tk
from tkinter import Button

# Global variables to control video playback
is_paused = False
is_running = True

def play_video():
    global is_paused
    is_paused = False

def pause_video():
    global is_paused
    is_paused = True

def stop_video():
    global is_running
    is_running = False
    window.quit()

def video_stream():
    global is_paused
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    # Continuously capture frames from the camera and display them
    while is_running:
        if not is_paused:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break

            cv2.imshow('USB Camera Feed', frame)

        # Allow tkinter to handle button events
        window.update()

        # Stop the video when the "Stop" button is clicked or the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()

# Create tkinter window
window = tk.Tk()
window.title("Camera Control")

# Create buttons
btn_pause = Button(window, text="Pause", command=pause_video)
btn_pause.pack(side="left")

btn_play = Button(window, text="Play", command=play_video)
btn_play.pack(side="left")

btn_stop = Button(window, text="Stop", command=stop_video)
btn_stop.pack(side="left")

# Start video capture in a separate function
video_stream()

# Start tkinter main loop
window.mainloop()