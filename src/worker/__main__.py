from worker.dispatcher import handlers
from src.queue import dequeue, enqueue, enqueue_failed

import time
from datetime import datetime, timezone
from src.redis import redis_client

MAX_RETRIES = 3


def process_job(job):
    job_type = job["type"]
    payload = job["payload"]

    handler = handlers.get(job_type)

    if not handler:
        print(f"Unknown job type: {job_type}")
        return

    handler(payload)


def worker_loop():
    print("Worker started...")

    while True:
        job = dequeue()  # get job from queue
        if not job:
            continue

        try:  # try to execute job
            job_id = job["id"]
            key = f"job:{job_id}:completed"  # makr job as done

            if not redis_client.setnx(key, "1"):  # set key if not exists
                print(f"Job {job_id} already fininshed, skipping")
                continue

            redis_client.expire(key, 3600)

            process_job(job)
            print(f"Successfully finished job {job["id"]}")

        except Exception as e:  # worker handles failures
            print(f"Job failed: {e}")

            redis_client.delete(
                key
            )  # delete key once job fails so setnx doesn't skip job on retry

            retries = job.get("retries", 0)

            if retries < MAX_RETRIES:
                job["retries"] = retries + 1
                delay = 2**retries  # add backooff between retries

                print(f"Retring job...[retry_count: {job['retries']}/3]")
                time.sleep(delay)

                enqueue(job)  # queue the job again

            else:  # add job to dlq
                print(print("Max retries reached. Sending to DLQ."))
                job["error"] = str(e)
                job["failed_at"] = datetime.now(timezone.utc).isoformat()

                enqueue_failed(job)


if __name__ == "__main__":
    worker_loop()


# what if i check the db for completed jobs?
