from process_job import process_job
from services.redis_service import Redis_servcie
from services.notification_service import Notification


redis_client = Redis_servcie()
pubsub = redis_client.pubsub_listener(channel_name="video_processing_channel")

notification = Notification()


def pubsub_listener():
    while True:

        message = next(pubsub.listen())

        # If message type is something different then just continue
        if message["type"] != "message":
            continue

        # Send notification to user that there's a new job
        userResponse = notification.send_notification(
            title="NEW JOB", message="Do you want to process it?"
        )

        if userResponse == "Yes":
            # Fetch Job
            job = redis_client.pop_queue(queue_name="video-processing-in-queue")

            # Send a notification that someone took the job and continue
            if not job:
                notification.send_notification(
                    title="Ohh No!", message="Someone else took the job already."
                )
                continue

            # Process the job
            process_job(job)
