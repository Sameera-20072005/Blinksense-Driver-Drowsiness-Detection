import cv2
import streamlit as st

def quick_camera_test():
    st.title("Quick Camera Test")
    
    # Test camera access
    if st.button("Test Camera"):
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                st.success("✅ Camera is working!")
                st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                st.error("❌ Cannot read from camera")
        else:
            st.error("❌ Cannot open camera")
        
        cap.release()

if __name__ == "__main__":
    quick_camera_test()
