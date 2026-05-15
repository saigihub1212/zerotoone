# pyrefly: ignore [missing-import]
import cv2
import numpy as np
from moviepy.editor import VideoFileClip

def find_placeholder_box(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    # Use thresholding to find dark/bright regions (placeholders are usually clear boxes)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter for the largest rectangular-ish contour in the middle of the screen
    h, w, _ = frame.shape
    best_box = None
    max_area = 0
    
    for cnt in contours:
        x, y, bw, bh = cv2.boundingRect(cnt)
        area = bw * bh
        
        # Check if it's a reasonable size (not the whole screen, not too small)
        if 100 < bw < w * 0.9 and 100 < bh < h * 0.9:
            # Check if it's roughly in the center area
            if area > max_area:
                max_area = area
                best_box = (x, y, bw, bh)
                
    return best_box

video_path = r"C:\Users\pc\Downloads\change the placeholders.mp4"
video = VideoFileClip(video_path)

times = [2, 24, 46]
results = {}

for t in times:
    print(f"Analyzing frame at {t}s...")
    frame = video.get_frame(t)
    box = find_placeholder_box(frame)
    if box:
        results[t] = box
        print(f"Found box at {t}s: x={box[0]}, y={box[1]}, w={box[2]}, h={box[3]}")
    else:
        print(f"Could not find box at {t}s automatically.")

print("\n--- DETECTED COORDINATES ---")
for t, box in results.items():
    print(f"Time {t}s: x={box[0]}, y={box[1]}, width={box[2]}, height={box[3]}")
