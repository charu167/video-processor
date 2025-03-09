from services.transcode_service import Transcode
from services.s3_service import S3Service
import os
import requests
import json

s3 = S3Service()
transcoder = Transcode()


def download_video(job):
    s3 = S3Service()

    bucket = job["Bucket"]
    key = job["Key"]
    local_filename = key.split("/")[-1]
    download_path = f"./downloads/{local_filename}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    s3.download_file(bucket, key, download_path)
    return download_path


def process_video(download_path):
    transcoder.convert_resolution(
        input_path=download_path,
        output_path="./downloads/temp360.mp4",
        width=640,
        height=360,
    )
    transcoder.convert_resolution(
        input_path=download_path,
        output_path="./downloads/temp480.mp4",
        width=854,
        height=480,
    )
    transcoder.convert_resolution(
        input_path=download_path,
        output_path="./downloads/temp720.mp4",
        width=1280,
        height=720,
    )
    transcoder.convert_resolution(
        input_path=download_path,
        output_path="./downloads/temp1080.mp4",
        width=1920,
        height=1080,
    )


def process_job(job):
    try:
        # Download and process video
        download_path = download_video(job)
        process_video(download_path)

        # Upload to S3
        s3.upload_file("./downloads/temp360.mp4", "v-out-bucket", "temp360.mp4")

        # Prepare notification payload
        payload = {
            "userId": 1,  # Extract from job instead of hardcoding
            "videoId": 'xyz.mp4',
            "status": "completed",
        }

        # Send notification request
        response = requests.post(
            "http://host.docker.internal:3001/notification/video-processed",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        # Check for request success
        if response.status_code == 200:
            print("Notification sent successfully")
        else:
            print(
                f"Failed to send notification: {response.status_code}, {response.text}"
            )

    except Exception as e:
        print(f"Error processing job: {str(e)}")
