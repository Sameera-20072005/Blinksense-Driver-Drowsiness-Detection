import subprocess
import sys

def install_with_mediapipe():
    """Install dependencies using MediaPipe instead of dlib"""
    packages = [
        "opencv-python",
        "mediapipe", 
        "numpy",
        "imutils",
        "scipy"
    ]
    
    for pkg in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"✓ {pkg} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {pkg}: {e}")
            return False
    
    print("\n✓ All packages installed successfully!")
    print("✓ MediaPipe-based drowsiness detection is ready!")
    return True

if __name__ == "__main__":
    install_with_mediapipe()
