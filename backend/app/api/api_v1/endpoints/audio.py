from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import FileResponse
import os
from pathlib import Path
import tempfile
import ffmpeg
import subprocess
import json

router = APIRouter()

# Fix the path to point to the correct static/audio directory
AUDIO_BASE_PATH = Path(__file__).parent.parent.parent.parent.parent / "static" / "audio"

def detect_silence_points(audio_path: str):
    """Detect silence at the beginning and end of audio file"""
    try:
        # Use ffmpeg to detect silence
        cmd = [
            'ffprobe', '-f', 'lavfi', '-i', 
            f'amovie={audio_path},silencedetect=noise=-30dB:duration=0.5',
            '-show_entries', 'tags=lavfi.silence_start,lavfi.silence_end',
            '-of', 'json', '-v', 'quiet'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None, None
            
        data = json.loads(result.stdout)
        silence_periods = []
        
        for packet in data.get('packets', []):
            tags = packet.get('tags', {})
            if 'lavfi.silence_start' in tags:
                start = float(tags['lavfi.silence_start'])
                silence_periods.append({'start': start, 'end': None})
            elif 'lavfi.silence_end' in tags and silence_periods:
                end = float(tags['lavfi.silence_end'])
                silence_periods[-1]['end'] = end
        
        # Get audio duration
        duration_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'json', audio_path]
        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = 0
        if duration_result.returncode == 0:
            duration_data = json.loads(duration_result.stdout)
            duration = float(duration_data.get('format', {}).get('duration', 0))
        
        # Find silence at beginning and end
        start_trim = 0
        end_trim = duration
        
        # Check for silence at the beginning (first 3 seconds)
        for period in silence_periods:
            if period['start'] <= 1.0 and period.get('end', 0) > 0.5:
                start_trim = min(period['end'], 3.0)  # Don't trim more than 3 seconds
                break
        
        # Check for silence at the end (last 3 seconds)
        for period in reversed(silence_periods):
            if period.get('end', 0) >= duration - 1.0 and period['start'] < duration:
                end_trim = max(period['start'], duration - 3.0)  # Don't trim more than 3 seconds
                break
        
        return start_trim, end_trim
        
    except Exception as e:
        print(f"Error detecting silence: {e}")
        return None, None

@router.post("/{book_abbr}/{chapter}/{verse}")
async def upload_audio(book_abbr: str, chapter: int, verse: int, file: UploadFile = File(...)):
    # Ensure directory exists
    audio_dir = AUDIO_BASE_PATH / book_abbr / str(chapter)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Convert to mp3 and detect silence for trimming
    audio_path = audio_dir / f"{verse}.mp3"
    temp_converted_path = None
    
    try:
        # First, convert to a temporary mp3 for silence detection
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
            temp_converted_path = temp_mp3.name
        
        # Initial conversion
        (
            ffmpeg
            .input(tmp_path)
            .output(temp_converted_path, audio_bitrate='64k', acodec='libmp3lame')
            .run(overwrite_output=True, quiet=True)
        )
        
        # Detect silence points
        start_trim, end_trim = detect_silence_points(temp_converted_path)
        
        # If we detected silence points, trim the audio
        if start_trim is not None and end_trim is not None and start_trim < end_trim:
            duration = end_trim - start_trim
            if duration > 1.0:  # Only trim if we have at least 1 second of audio left
                (
                    ffmpeg
                    .input(temp_converted_path, ss=start_trim, t=duration)
                    .output(str(audio_path), audio_bitrate='64k', acodec='libmp3lame')
                    .run(overwrite_output=True, quiet=True)
                )
                print(f"Audio trimmed: removed {start_trim:.2f}s from start, {end_trim:.2f}s total duration")
            else:
                # If trimming would make audio too short, use original
                os.rename(temp_converted_path, str(audio_path))
                temp_converted_path = None
        else:
            # If silence detection failed, use the converted file as-is
            os.rename(temp_converted_path, str(audio_path))
            temp_converted_path = None
            
    except Exception as e:
        # Cleanup temp files
        if temp_converted_path and os.path.exists(temp_converted_path):
            os.remove(temp_converted_path)
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {e}")
    
    # Cleanup temp files
    if temp_converted_path and os.path.exists(temp_converted_path):
        os.remove(temp_converted_path)
    os.remove(tmp_path)
    
    return {"detail": "Audio uploaded, trimmed, and compressed successfully."}

@router.get("/{book_abbr}/{chapter}/{verse}")
async def get_audio(book_abbr: str, chapter: int, verse: int):
    audio_path = AUDIO_BASE_PATH / book_abbr / str(chapter) / f"{verse}.mp3"
    print(f"Audio endpoint: Looking for audio at: {audio_path}")
    print(f"Audio endpoint: Path exists: {audio_path.exists()}")
    print(f"Audio endpoint: AUDIO_BASE_PATH: {AUDIO_BASE_PATH}")
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found.")
    
    # Create FileResponse with explicit CORS headers
    response = FileResponse(audio_path, media_type="audio/mpeg")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@router.head("/{book_abbr}/{chapter}/{verse}")
async def head_audio(book_abbr: str, chapter: int, verse: int):
    audio_path = AUDIO_BASE_PATH / book_abbr / str(chapter) / f"{verse}.mp3"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found.")
    
    # Create Response with explicit CORS headers
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@router.options("/{book_abbr}/{chapter}/{verse}")
async def options_audio(book_abbr: str, chapter: int, verse: int):
    """Handle CORS preflight requests"""
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"  # Cache preflight for 24 hours
    return response

@router.get("/")
async def read_audio():
    return [] 