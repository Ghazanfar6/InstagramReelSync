from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import os
from config import PROCESSED_VIDEO_DIR

def crop_video(input_path, output_path, crop_percent=0.03):
    try:
        with VideoFileClip(input_path) as video:
            width, height = video.size
            crop_x = int(width * crop_percent)
            crop_y = int(height * crop_percent)
            cropped_video = video.crop(x1=crop_x, y1=crop_y, x2=width-crop_x, y2=height-crop_y)
            cropped_video.write_videofile(output_path, codec='libx264')
    except Exception as e:
        print(f"Error cropping video: {e}")

def add_border(input_path, output_path, border_size=10):
    try:
        with VideoFileClip(input_path) as video:
            bordered_video = video.margin(border_size, color=(0, 0, 0))
            bordered_video.write_videofile(output_path, codec='libx264')
    except Exception as e:
        print(f"Error adding border to video: {e}")

def overlay_logo(input_path, output_path, logo_path, alpha=0.5):
    try:
        with VideoFileClip(input_path) as video:
            logo = (ImageClip(logo_path)
                    .set_duration(video.duration)
                    .resize(height=video.size[1] // 10)  # Resize logo to 10% of the video height
                    .set_position(("right", "top"))
                    .set_opacity(alpha))
            final_video = CompositeVideoClip([video, logo])
            final_video.write_videofile(output_path, codec='libx264')
    except Exception as e:
        print(f"Error overlaying logo on video: {e}")

def process_video(input_video_path):
    # Logic to process the video
    processed_video_path = os.path.join(PROCESSED_VIDEO_DIR, 'processed_video.mp4')
    # Save the processed video to the new directory
    # ...processing logic...
    return processed_video_path
