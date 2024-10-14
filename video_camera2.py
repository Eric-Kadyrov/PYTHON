import cv2

# Open a connection to the USB camera (0 is usually the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video source.")
    exit()

# Create a window to display the video
cv2.namedWindow('USB Camera Feed', cv2.WINDOW_NORMAL)

# Capture video in a loop
while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # If the frame was not grabbed successfully, break the loop
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Display the frame in the created window
    cv2.imshow('USB Camera Feed', frame)

    # Check if the window has been closed or the 'q' key has been pressed to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()