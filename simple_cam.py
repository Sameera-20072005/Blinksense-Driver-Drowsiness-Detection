import cv2

# Test camera directly
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not found. Trying camera 1...")
    cap = cv2.VideoCapture(1)

if cap.isOpened():
    print("Camera working! Press 'q' to quit")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera Test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("No frame")
            break
    cap.release()
    cv2.destroyAllWindows()
else:
    print("No camera available")