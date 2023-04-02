from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
from threading import Thread


executor = ProcessPoolExecutor(max_workers=5)
logger = logging.getLogger(__name__)

def submit(fn, *args, **kwargs):
    logger.info(f"Starting a background task for fn: {fn}")
    thread = Thread(target=fn, args=args, kwargs=kwargs)
    thread.start()
