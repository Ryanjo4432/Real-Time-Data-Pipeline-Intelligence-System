import schedule
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import pipeline


def job():
    try:
        pipeline.run_pipeline()
    except Exception as e:
        print(f"job failed: {e}")


# run every 5 minutes
schedule.every(5).minutes.do(job)

print("scheduler running — pipeline fires every 5 min. ctrl+c to stop")
job()  # run immediately on start

while True:
    schedule.run_pending()
    time.sleep(10)
