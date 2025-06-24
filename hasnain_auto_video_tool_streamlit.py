# hasnain_auto_video_tool_streamlit.py

import os
import traceback
import streamlit as st
from moviepy.editor import *

st.set_page_config(page_title="🎬 Hasnain Auto Video Tool", layout="centered")
st.title("🎬 Hasnain Auto Video Tool Pro")
st.markdown("""
This advanced version supports:
- ✅ Audio narration upload
- ✅ Images & video visuals
- ✅ Optional animated text
- ✅ Subtitles (.srt) support
- ✅ Auto background music
""")

VALID_LICENSE_KEY = "hasnain2025"
key = st.text_input("🔐 Enter License Key", type="password")
if key != VALID_LICENSE_KEY:
    st.warning("Please enter a valid license key to use this tool.")
    st.stop()

audio_file = st.file_uploader("🎧 Upload Audio (MP3 or WAV)", type=["mp3", "wav"])
visual_files = st.file_uploader("🖼️ Upload Images/Videos (JPG, PNG, MP4, MOV)", type=["jpg", "png", "mp4", "mov"], accept_multiple_files=True)
subtitle_file = st.file_uploader("📝 Upload Subtitles (.srt, optional)", type=["srt"])
bg_music_file = st.file_uploader("🎶 Upload Background Music (optional)", type=["mp3", "wav"])
add_text = st.checkbox("Add Animated Text")

def parse_srt(srt_text):
    try:
        from moviepy.video.tools.subtitles import SubtitlesClip
        import re
        pattern = r"(\d+)\s+([\d:,]+)\s+-->\s+([\d:,]+)\s+(.+?)(?=\n\d+|\Z)"
        entries = re.findall(pattern, srt_text, re.DOTALL)
        subs = [
            ((start.replace(',', '.'), end.replace(',', '.')), txt.strip().replace('\n', ' '))
            for _, start, end, txt in entries
        ]
        return SubtitlesClip(subs, lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white'))
    except Exception as e:
        st.warning("Subtitle parsing failed.")
        return None

if st.button("🚀 Create Video"):
    if not audio_file or not visual_files:
        st.error("Please upload both audio and at least one image/video file.")
        st.stop()

    try:
        os.makedirs("temp", exist_ok=True)
        audio_path = f"temp/{audio_file.name}"
        with open(audio_path, "wb") as f:
            f.write(audio_file.read())

        narration = AudioFileClip(audio_path)
        visuals = []

        for uploaded in visual_files:
            temp_path = f"temp/{uploaded.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded.read())
            if uploaded.name.lower().endswith((".jpg", ".png")):
                visuals.append(ImageClip(temp_path).set_duration(5).resize(height=720))
            elif uploaded.name.lower().endswith((".mp4", ".mov")):
                visuals.append(VideoFileClip(temp_path).subclip(0, 5).resize(height=720))

        if not visuals:
            st.error("No valid visuals were processed.")
            st.stop()

        final_visual = concatenate_videoclips(visuals, method="compose")

        if add_text:
            try:
                txt = TextClip("Never Give Up!", fontsize=70, color='white', method='caption', size=final_visual.size)
                txt = txt.set_duration(5).set_position('center').fadein(1)
                final_visual = CompositeVideoClip([final_visual, txt.set_start(2)])
            except Exception as e:
                st.warning(f"Animated text overlay failed: {e}")

        # Subtitles
        subtitle_clip = None
        if subtitle_file:
            srt_text = subtitle_file.read().decode('utf-8')
            subtitle_clip = parse_srt(srt_text)

        if subtitle_clip:
            final_visual = CompositeVideoClip([final_visual, subtitle_clip.set_position(('center','bottom'))])

        # Background music
        if bg_music_file:
            bg_path = f"temp/{bg_music_file.name}"
            with open(bg_path, "wb") as f:
                f.write(bg_music_file.read())
            bg_music = AudioFileClip(bg_path).volumex(0.2)
            final_audio = CompositeAudioClip([narration.volumex(1.0), bg_music])
        else:
            final_audio = narration

        final_video = final_visual.set_audio(final_audio)
        output_path = "final_output.mp4"
        final_video.write_videofile(output_path, fps=24)

        with open(output_path, "rb") as f:
            st.success("✅ Video Created Successfully!")
            st.download_button("📥 Download Video", f, file_name="final_output.mp4")

    except Exception as e:
        st.error("An error occurred during video creation.")
        st.text(traceback.format_exc())
