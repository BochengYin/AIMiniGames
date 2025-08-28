#!/usr/bin/env python3
"""
Stop Notification Hook
Plays system sound when tasks are completed
"""

import sys
import subprocess
import os

def play_notification_sound():
    """Play system notification sound on macOS"""
    try:
        # Use macOS system sound for task completion
        # You can customize the sound file path
        sound_options = [
            "/System/Library/Sounds/Glass.aiff",        # Glass sound (completion)
            "/System/Library/Sounds/Purr.aiff",         # Purr sound (gentle)
            "/System/Library/Sounds/Tink.aiff",         # Tink sound (subtle)
            "/System/Library/Sounds/Hero.aiff",         # Hero sound (achievement)
        ]
        
        # Use Glass sound as default (sounds like task completion)
        sound_file = sound_options[0]
        
        if os.path.exists(sound_file):
            subprocess.run(["afplay", sound_file], check=True, capture_output=True)
            print("🔔 Task completed! Notification sound played.")
        else:
            # Fallback to system beep
            subprocess.run(["osascript", "-e", "beep"], check=True, capture_output=True)
            print("🔔 Task completed! System beep played.")
            
    except subprocess.CalledProcessError:
        print("⚠️ Could not play notification sound")
    except Exception as e:
        print(f"⚠️ Notification error: {e}")

def check_task_completion():
    """Check if the TodoWrite indicates task completion"""
    # This hook is triggered after TodoWrite operations
    # We can assume a task status change occurred
    print("📋 Task status updated")
    play_notification_sound()

if __name__ == "__main__":
    check_task_completion()