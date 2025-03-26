import os
import json
import shutil
import requests
from typing import Dict, Optional
from pathlib import Path
from config.config import LOCAL_URL
from services.transcode_service import Transcode
from services.s3_service import S3Service

# Initialize services
s3 = S3Service()
transcoder = Transcode()

# Constants
OUTPUT_BUCKET = "v-out-bucket"
DOWNLOAD_DIR = "./downloads"
PRESIGNED_URL_EXPIRY = 604800  # 7 days in seconds


def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)


def download_video(job: Dict) -> str:
    """Download video from S3 to local storage"""
    bucket = job.get("bucket")
    key = job.get("fileKey")

    if not bucket or not key:
        raise ValueError("Missing Bucket or Key in job data")

    local_filename = key.split("/")[-1]
    download_path = f"{DOWNLOAD_DIR}/{local_filename}"
    ensure_directory_exists(DOWNLOAD_DIR)

    if not s3.download_file(bucket, key, download_path):
        raise RuntimeError(f"Failed to download {key} from {bucket}")

    return download_path


def process_video(input_path: str) -> Dict[str, str]:
    """Convert video to multiple resolutions"""
    resolutions = {
        "360p": {"path": f"{DOWNLOAD_DIR}/temp360.mp4", "width": 640, "height": 360},
        "480p": {"path": f"{DOWNLOAD_DIR}/temp480.mp4", "width": 854, "height": 480},
        "720p": {"path": f"{DOWNLOAD_DIR}/temp720.mp4", "width": 1280, "height": 720},
        "1080p": {
            "path": f"{DOWNLOAD_DIR}/temp1080.mp4",
            "width": 1920,
            "height": 1080,
        },
    }

    for res, config in resolutions.items():
        transcoder.convert_resolution(
            input_path=input_path,
            output_path=config["path"],
            width=config["width"],
            height=config["height"],
        )

    return {res: config["path"] for res, config in resolutions.items()}


def upload_resolutions(
    user_id: str, resolutions: Dict[str, str]
) -> Dict[str, Dict[str, str]]:
    """Upload processed videos to S3 and return their metadata"""
    output_videos = {}

    for res, file_path in resolutions.items():
        output_key = f"output/{user_id}/output_{res}.mp4"
        presigned_url = s3.upload_file(
            local_path=file_path,
            bucket=OUTPUT_BUCKET,
            object_name=output_key,
            expires_in=PRESIGNED_URL_EXPIRY,
        )

        if not presigned_url:
            print(f"Failed to upload {res} resolution")
            continue

        output_videos[res] = {
            "s3_path": f"s3://{OUTPUT_BUCKET}/{output_key}",
            "download_url": presigned_url,
        }

    return output_videos


def send_notification(payload: Dict) -> bool:
    """Send processing completion notification"""
    try:
        response = requests.post(
            f"http://{LOCAL_URL}:3001/notification/video-processed",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Notification failed: {str(e)}")
        return False


def cleanup():
    """Remove temporary files"""
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)


def process_job(job: Dict) -> None:
    """Main job processing workflow"""
    try:
        user_id = job.get("userId")
        if not user_id:
            raise ValueError("Missing userId in job data")

        # Download and process video
        download_path = download_video(job)
        resolutions = process_video(download_path)

        # Upload to S3 and get URLs
        output_videos = upload_resolutions(user_id, resolutions)

        if not output_videos:
            raise RuntimeError("No videos were successfully uploaded")

        # Prepare and send notification
        payload = {
            "userId": user_id,
            "status": "completed",
            "outputVideos": output_videos,
        }

        if not send_notification(payload):
            print("Notification failed, but processing completed successfully")

    except Exception as e:
        print(f"Error processing job: {str(e)}")
        # Consider adding error notification here
    finally:
        cleanup()
