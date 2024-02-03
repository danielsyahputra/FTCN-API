from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import subprocess
import os

app = FastAPI()

processing_lock = False

def run_video_detection(video_path: str):
    global processing_lock
    try:
        processing_lock = True
        cmd = f"python test_on_raw_video.py {video_path} output"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error running video detection: {str(e)}")
    finally:
        # Release the lock after video processing is complete
        processing_lock = False

@app.post("/detect-video/", tags=["Detection"])
async def detect_video(background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    global processing_lock
    # Check if a video processing task is already in progress
    if processing_lock:
        return JSONResponse(content={"message": "System is currently processing a video, come back later."}, status_code=400)
    
    temp_video_path = f"examples/{video.filename}"
    with open(temp_video_path, "wb") as temp_video:
        shutil.copyfileobj(video.file, temp_video)

    # Run video detection in the background
    background_tasks.add_task(run_video_detection, temp_video_path)

    return JSONResponse(content={"message": "Video detection in progress"}, status_code=202)

@app.post("/video-status/", tags=["Status"])
async def video_status(video: UploadFile = File(...)):
    # Check if the video file exists in the output directory to determine the status
    output_path = f"output/{video.filename.split('.')[0]}.avi"  # Update with your actual output directory
    if os.path.exists(output_path):
        return JSONResponse(content={"message": "Video detection complete", "output_path": output_path, "status": "success"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Video detection in progress", "status": "failed"}, status_code=202)

# Redirect the root path ("/") to the "/docs" path
@app.get("/", include_in_schema=False)
async def read_root():
    return RedirectResponse(url="/docs")
