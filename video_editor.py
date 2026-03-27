import cv2
import os
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip
import tempfile

class VideoAIEditor:
    def __init__(self):
        self.scenes = []
    
    def detect_scenes(self, video_path):
        """Video mein scenes detect karo"""
        try:
            cap = cv2.VideoCapture(video_path)
            scenes = []
            frame_count = 0
            prev_frame = None
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 30 == 0 and prev_frame is not None:
                    gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    diff = cv2.absdiff(gray_current, gray_prev).mean()
                    
                    if diff > 30:
                        time_in_seconds = frame_count / fps
                        scenes.append(round(time_in_seconds, 2))
                
                if frame_count % 30 == 0:
                    prev_frame = frame.copy()
                
                frame_count += 1
            
            cap.release()
            return scenes
            
        except Exception as e:
            print(f"Error in scene detection: {e}")
            return []
    
    def extract_audio(self, video_path, output_audio_path):
        """Video se audio alag karo"""
        try:
            video = VideoFileClip(video_path)
            if video.audio is not None:
                video.audio.write_audiofile(output_audio_path, logger=None)
                video.close()
                return True
            return False
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return False
    
    def add_captions(self, video_path, transcription, output_path):
        """Bina TextClip ke - bas original video copy karo"""
        try:
            print(f"📹 Copying video...")
            
            # Direct copy without captions
            video = VideoFileClip(video_path)
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                verbose=False,
                logger=None
            )
            video.close()
            
            # Save transcription to a text file
            txt_path = output_path.replace('.mp4', '_transcription.txt')
            with open(txt_path, 'w') as f:
                f.write(transcription)
            
            print(f"✅ Video copied! Transcription saved to {txt_path}")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def create_highlight_reel(self, video_path, scenes, output_path, duration_per_scene=5):
        """Scenes se highlight reel banao"""
        try:
            if not scenes:
                print("No scenes to create highlight reel")
                return False
                
            video = VideoFileClip(video_path)
            clips = []
            
            for scene_time in scenes[:3]:  # Max 3 scenes
                start = max(0, scene_time - 2)
                end = min(video.duration, scene_time + duration_per_scene)
                clip = video.subclip(start, end)
                clips.append(clip)
            
            if clips:
                from moviepy.editor import concatenate_videoclips
                final = concatenate_videoclips(clips)
                
                final.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=video.fps,
                    verbose=False,
                    logger=None
                )
                
                video.close()
                final.close()
                return True
            return False
            
        except Exception as e:
            print(f"Error creating highlight reel: {e}")
            return False
