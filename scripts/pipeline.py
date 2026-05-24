import logging
import os
from datetime import datetime

import extract
import transform
import load

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def run_pipeline():
    logging.info("pipeline started")
    print(f"\n{'='*40}\nPipeline run: {datetime.utcnow()}\n{'='*40}")

    try:
        raw = extract.run()
        logging.info("extract done")

        transformed = transform.run(raw)
        logging.info("transform done")

        load.run(transformed)
        logging.info("load done")

        print("pipeline complete")
    except Exception as e:
        logging.error(f"pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
