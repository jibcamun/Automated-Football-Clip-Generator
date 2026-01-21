from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import os

TARGET_W = 1080
TARGET_H = 1920
TARGET_RATIO = TARGET_W / TARGET_H
MAX_DURATION = 60.0  # seconds

def make_vertical_clip(path, max_duration=None):
    """
    Load a clip, resize/crop to TARGET_W x TARGET_H, and trim to max_duration.
    Returns a moviepy VideoFileClip.
    """
    clip = VideoFileClip(path)
    w, h = clip.size
    ratio = w / h

    # Resize then center-crop so we keep vertical orientation
    if ratio > TARGET_RATIO:
        # clip is relatively wider than target (too wide) -> set height and crop width
        clip = clip.resize(height=TARGET_H)
        # center crop width
        new_w, new_h = clip.size
        x_center = new_w / 2
        x1 = max(0, x_center - TARGET_W / 2)
        x2 = x1 + TARGET_W
        clip = clip.crop(x1=x1, x2=x2, y1=0, y2=TARGET_H)
    else:
        # clip is relatively taller or correct -> set width and crop height
        clip = clip.resize(width=TARGET_W)
        new_w, new_h = clip.size
        y_center = new_h / 2
        y1 = max(0, y_center - TARGET_H / 2)
        y2 = y1 + TARGET_H
        clip = clip.crop(x1=0, x2=TARGET_W, y1=y1, y2=y2)

    # Trim if requested
    if max_duration is not None and clip.duration > max_duration:
        clip = clip.subclip(0, max_duration)

    return clip

def build_short_from_folder(input_dir, max_total_duration=MAX_DURATION, music_path=None, prefer_sort="longest"):
    """
    Find video files in input_dir, transform to vertical format and concatenate until max_total_duration.
    prefer_sort: "longest" or "shortest" (controls ordering)
    Returns final VideoFileClip
    """
    # gather video files (simple filter)
    exts = (".mp4", ".mov", ".mkv", ".avi", ".webm")
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith(exts)]
    if not files:
        raise FileNotFoundError(f"No video files found in {input_dir}")

    # sort
    clips_meta = []
    for p in files:
        try:
            c = VideoFileClip(p)
            clips_meta.append((p, c.duration))
            c.close()
        except Exception:
            # skip unreadable
            continue

    if not clips_meta:
        raise RuntimeError("No readable clips found.")

    if prefer_sort == "longest":
        clips_meta.sort(key=lambda x: -x[1])
    else:
        clips_meta.sort(key=lambda x: x[1])

    selected = []
    total = 0.0
    for p, dur in clips_meta:
        remain = max_total_duration - total
        if remain <= 0:
            break
        take = min(dur, remain)
        clip = make_vertical_clip(p, max_duration=take)
        selected.append(clip)
        total += clip.duration

    final = concatenate_videoclips(selected, method="compose")

    # attach music if requested
    if music_path:
        music = AudioFileClip(music_path).volumex(0.6)
        # if music longer than video, subclip it
        if music.duration > final.duration:
            music = music.subclip(0, final.duration)
        # combine with existing audio (if any)
        if final.audio:
            combined = CompositeAudioClip([final.audio.volumex(0.9), music])
            final = final.set_audio(combined)
        else:
            final = final.set_audio(music)

    return final

def export_clip(clip, out_path, bitrate="2500k"):
    # MoviePy uses ffmpeg under the hood
    # Use reasonable settings for Shorts
    clip.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        bitrate=bitrate,
        threads=4,
        preset="medium",
        ffmpeg_params=["-movflags", "+faststart"]
    )
    clip.close()
