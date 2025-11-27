# if you read this, remember "Ctrl + Shift + Backspace" to remove gaps in the timeline

import sys
import os

modules_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"

if os.path.isdir(modules_path) and modules_path not in sys.path:
    sys.path.append(modules_path)

import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")


# -------------- VERIFICATIONS ---------------

if not resolve:
    print("Error: resolve empty")
    raise SystemExit(1)

project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()

if not project:
    print("Error: no project opened")
    raise SystemExit(1)

timeline = project.GetCurrentTimeline() 

if not timeline:
    print("Error: no timeline opened")
    raise SystemExit(1)

# -------------------------------------------


print(f"Searching gaps in timeline {timeline.GetName()}\n")

fps = timeline.GetSetting("timelineFrameRate")
if not fps:
    fps = 24.0
else:
    fps = float(fps)

def frame_to_timecode(frame, fps):
    """Convertit un nombre de frames en timecode HH:MM:SS:FF"""
    total_seconds = frame / fps
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frames = int(frame % fps)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

def frames_to_duration(frames, fps):
    """Convertit un nombre de frames en durée"""
    total_seconds = frames / fps
    if total_seconds < 60:
        return f"{total_seconds:.2f}s"
    elif total_seconds < 3600:
        return f"{int(total_seconds // 60)}m {int(total_seconds % 60)}s"
    else:
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

track_count = timeline.GetTrackCount("video")

if track_count == 0:
    print("0 video tracks in the timeline")
    raise SystemExit(1)

total_gaps = 0
total_gap_frames = 0
all_gaps = []

for track_index in range(1, track_count + 1):
    clips = timeline.GetItemListInTrack("video", track_index)
    if not clips or len(clips) == 0:
        continue
    sorted_clips = sorted(clips, key=lambda clip: clip.GetStart())
    track_gaps = []
    previous_end = None
    
    for i, clip in enumerate(sorted_clips):
        clip_start = clip.GetStart()
        clip_duration = clip.GetDuration()
        clip_end = clip_start + clip_duration
        clip_name = clip.GetName()
        if previous_end is not None:
            gap = clip_start - previous_end
            if gap > 0:
                gap_info = {
                    'track': track_index,
                    'start': previous_end,
                    'end': clip_start,
                    'duration': gap,
                    'before_clip': sorted_clips[i-1].GetName() if i > 0 else "Start",
                    'after_clip': clip_name
                }
                track_gaps.append(gap_info)
                total_gaps += 1
                total_gap_frames += gap
        previous_end = clip_end


    if track_gaps:
        track_name = timeline.GetTrackName("video", track_index)
        print(f"Track {track_index} ({track_name if track_name else 'Unnamed'}): {len(track_gaps)} gap(s) found")
        
        for gap in track_gaps:
            print(f"   Gap: {frames_to_duration(gap['duration'], fps)} ({gap['duration']} frames)")
            print(f"      Position: {frame_to_timecode(gap['start'], fps)} → {frame_to_timecode(gap['end'], fps)}")
            print(f"      Between: '{gap['before_clip']}' and '{gap['after_clip']}'")
            print()
        all_gaps.extend(track_gaps)

# -------------------------------------------

print("=" * 60)
if total_gaps > 0:
    print(f"Summary:")
    print(f"   Total gaps found: {total_gaps}")
    print(f"   Total gap duration: {frames_to_duration(total_gap_frames, fps)} ({total_gap_frames} frames)")
    print()
else:
    print(f"No gaps found")
print("=" * 60)

