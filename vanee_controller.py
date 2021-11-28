import time
import threading
import logging
import queue
import signal
import sys
from datetime import datetime, timedelta

import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(name)s:%(message)s")


MAX_HIGH_TIME = timedelta(minutes=60)
HIGH_TIME_STEP = timedelta(minutes=15)

RELAY_PIN = 37
INPUT_PIN = 7

RELAY_LOW_STATE = GPIO.HIGH
RELAY_HIGH_STATE = GPIO.LOW


def button_watcher(q, quit_event):
    logger = logging.getLogger("button")
    while True:
        if quit_event.is_set():
            return

        input_state = GPIO.input(INPUT_PIN)
        if input_state:
            logger.info('button press detected')
            q.put(True)
            time.sleep(0.2)

def relay_switcher(q, quit_event):
    next_low_time = datetime.utcnow()
    logger = logging.getLogger("relay")
    while True:
        if quit_event.is_set():
            return

        if not q.empty():
            item = q.get()
            next_low_time = min(
                datetime.utcnow() + MAX_HIGH_TIME,
                max(datetime.utcnow(), next_low_time) + HIGH_TIME_STEP
            )
            logger.info("set next low time to %s", next_low_time)

        if next_low_time > datetime.utcnow():
            logger.info("%d seconds until next low time, set relay to high", (next_low_time - datetime.utcnow()).total_seconds())
            GPIO.output(RELAY_PIN, RELAY_HIGH_STATE)
        else:
            logger.info("next low time is in the past, set relay to low")
            GPIO.output(RELAY_PIN, RELAY_LOW_STATE)

        time.sleep(1)

def cleanup(t1, t2):
    logger = logging.getLogger("cleanup")
    logger.info("attempting to close threads")
    quit_event.set()
    t1.join()
    t2.join()
    logger.info("threads successfully closed")
    logger.info("shutting down... setting relay to low")
    GPIO.output(RELAY_PIN, RELAY_LOW_STATE)
    time.sleep(1)
    
    logger.info("calling GPIO.cleanup")
    GPIO.cleanup()

    sys.exit()

if __name__ == '__main__':
    logger = logging.getLogger("main")
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    logger.info("startup... setting relay to low")
    GPIO.output(RELAY_PIN, RELAY_LOW_STATE)

    q = queue.Queue(10)

    quit_event = threading.Event()
    quit_event.clear()

    t1 = threading.Thread(name='button_watcher', target=button_watcher, args=(q, quit_event))
    t2 = threading.Thread(name='relay_switcher', target=relay_switcher, args=(q, quit_event))

    logger.info("starting threads")
    t1.start()
    t2.start()

    signal.signal(signal.SIGTERM, lambda *args: cleanup(t1, t2))

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        cleanup(t1, t2)
