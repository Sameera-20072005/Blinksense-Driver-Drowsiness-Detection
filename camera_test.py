import cv2
import sys

def test_camera():
    print("Testing camera access...")
    
    # Try different camera indices
    for i in range(3):
        print(f"Trying camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"SUCCESS: Camera {i} works!")
                cap.release()
                return i
            else:
                print(f"ERROR: Camera {i} opened but no frame")
        else:
            print(f"ERROR: Camera {i} failed to open")
        cap.release()
    
    print("ERROR: No working camera found")
    return None

if __name__ == "__main__":
    working_camera = test_camera()
    if working_camera is not None:
        print(f"Use camera index: {working_camera}")
    else:
        print("Please check your camera connection and permissions")