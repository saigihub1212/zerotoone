from PIL import Image

# Pillow compatibility fix
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    CompositeVideoClip
)

# Load template video
video = VideoFileClip(
    r"C:\Users\pc\Downloads\change the placeholders.mp4"
)

# ========================================================
# UPDATED CONFIGURATION (Full-Screen 1080x1920)
# ========================================================
# Setting X and Y to 0 and size to 1080x1920 to cover the whole screen
X_POS = 0
Y_POS = 0
WIDTH = 1080
HEIGHT = 1920

placeholders = [
    {
        "image": "image1.png",
        "start": 0,      # Start at 1s
        "end": 4,        # End at 4s
        "x": X_POS,
        "y": Y_POS,
        "size": (WIDTH, HEIGHT)
    },
    {
        "image": "image2.png",
        "start": 22,     # Start at 23s
        "end": 25,       # End at 25s
        "x": X_POS,
        "y": Y_POS,
        "size": (WIDTH, HEIGHT)
    },
    {
        "image": "image3.png",
        "start": 45,     # Start at 45s
        "end": video.duration,
        "x": X_POS,
        "y": Y_POS,
        "size": (WIDTH, HEIGHT)
    }
]

# Create composite layers
all_clips = [video]

for p in placeholders:
    duration = p["end"] - p["start"]
    image_clip = (
        ImageClip(p["image"])
        .resize(newsize=p["size"]) # Full screen size
        .set_position((p["x"], p["y"]))
        .set_start(p["start"])
        .set_duration(duration)
    )
    all_clips.append(image_clip)

# Final composition
final = CompositeVideoClip(all_clips)

print(f"Rendering video with FULL-SCREEN images ({WIDTH}x{HEIGHT})...")
final.write_videofile(
    "output.mp4",
    codec="libx264",
    audio_codec="aac",
    fps=video.fps,
    temp_audiofile="temp-audio-v9.m4a",
    remove_temp=True
)
print("Done! output.mp4 generated with full-screen images.")