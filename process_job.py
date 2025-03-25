from services.transcode_service import Transcode
from services.s3_service import S3Service
import os
import requests
import json

s3 = S3Service()
transcoder = Transcode()


def download_video(job):
    bucket = job.get("bucket")
    key = job.get("fileKey")

    if not bucket or not key:
        raise ValueError("Missing Bucket or Key in job data")

    local_filename = key.split("/")[-1]
    download_path = f"./downloads/{local_filename}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)

    # ✅ Download the file
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
        user_id = job.get("userId")  # Extract userId from job data

        if not user_id:
            print("Invalid job data: Missing userId or jobId")
            return

        # Download and process video
        download_path = download_video(job)
        process_video(download_path)

        # ✅ Upload processed videos to structured S3 paths
        resolutions = {
            "360p": "./downloads/temp360.mp4",
            "480p": "./downloads/temp480.mp4",
            "720p": "./downloads/temp720.mp4",
            "1080p": "./downloads/temp1080.mp4",
        }

        output_bucket = "v-out-bucket"

        # Upload to S3
        for res, file_path in resolutions.items():
            output_key = f"output/{user_id}/output_{res}.mp4"
            s3.upload_file(file_path, output_bucket, output_key)

        # ✅ Prepare notification payload with correct video paths
        payload = {
            "userId": user_id,
            # "jobId": job_id,
            "status": "completed",
            "outputVideos": {
                res: f"s3://{output_bucket}/{output_key}"
                for res, output_key in resolutions.items()
            },
        }

        # Send notification request
        response = requests.post(
            "http://localhost:3001/notification/video-processed",
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
