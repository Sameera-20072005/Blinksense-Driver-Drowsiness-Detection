#!/usr/bin/env python3
"""
BlinkSense - Driver Drowsiness Detection System
Simple launcher script
"""

import subprocess
import sys
import os

def main():
    print("🚗 Starting BlinkSense - Driver Drowsiness Detection System")
    print("=" * 60)
    
    try:
        # Run the web application
        subprocess.run([sys.executable, "drowsiness_web_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 BlinkSense stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your camera is connected")
        print("2. Check if required packages are installed: pip install flask opencv-python numpy")
        print("3. Try running: python drowsiness_web_app.py")

if __name__ == "__main__":
    main()