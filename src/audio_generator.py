import sys
import asyncio
import os
import subprocess
import edge_tts

# Define voices (Microsoft Edge high quality neural voices)
HOST_VOICE = "en-US-ChristopherNeural"
GUEST_VOICE = "en-US-JennyNeural"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Find FFmpeg based on OS
if sys.platform == "win32":
    FFMPEG_EXE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe", "ffmpeg-8.0.1-full_build", "bin", "ffmpeg.exe")
else:
    FFMPEG_EXE = "ffmpeg"

async def generate_audio_for_line(text: str, voice: str, output_path: str):
    """Generates an MP3 file for a single line of text."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_podcast_audio(script: list[dict], host_voice=HOST_VOICE, guest_voice=GUEST_VOICE, output_filename="final_podcast.mp3") -> str:
    """Takes a script list and generates the full podcast audio file."""
    
    print("Starting audio generation...")
    # 1. Generate individual audio files for each line
    temp_files = []
    
    for i, line in enumerate(script):
        speaker = line.get("speaker")
        text = line.get("text")
        
        # Assign voice
        voice = host_voice if speaker == "Host" else guest_voice
        
        # File path for this line
        temp_path = os.path.join(OUTPUT_DIR, f"temp_line_{i}.mp3")
        temp_files.append(temp_path)
        
        print(f"Generating audio for line {i+1}/{len(script)} ({speaker})...")
        asyncio.run(generate_audio_for_line(text, voice, temp_path))

    print("\nStitching audio tracks together using FFmpeg...")
    
    list_file_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(list_file_path, 'w', encoding="utf-8") as f:
        for file in temp_files:
            safe_path = os.path.abspath(file).replace('\\', '/')
            f.write(f"file '{safe_path}'\n")

    final_output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    if os.path.exists(final_output_path):
        os.remove(final_output_path)
        
    print(f"Using FFmpeg at: {FFMPEG_EXE}")
    
    # Run the exact target command via subprocess array (safer than powershell direct string execution)
    command = [
        FFMPEG_EXE,
        "-f", "concat",
        "-safe", "0",
        "-i", list_file_path,
        "-c", "copy",
        final_output_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully exported final podcast to: {final_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during audio concatenation: {e.stderr.decode('utf-8')}")
        return ""
    
    # Cleanup temporary files
    if os.path.exists(list_file_path):
        os.remove(list_file_path)
        
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            
    return final_output_path

if __name__ == "__main__":
    test_script = [
        {"speaker": "Host", "text": "Hello, welcome to the test podcast! Today we are testing our brand new audio generation pipeline."},
        {"speaker": "Guest", "text": "That's right! I'm the guest, and I sound incredibly realistic thanks to the Edge TTS engine."},
        {"speaker": "Host", "text": "Amazing. Let's make sure the audio gets stitched together properly."},
    ]
    create_podcast_audio(test_script, "test_output.mp3")
