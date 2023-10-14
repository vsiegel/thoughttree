from datetime import datetime
from pathlib import Path


class EventLog:
    def __init__(self, toplevel, *events):

        logdir = Path.home()/"logs"/"thoughttree"
        if not logdir.exists():
            logdir.mkdir(parents=True, exist_ok=True)
        event_log_path = logdir/f"thoughttree-events-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
        event_log = open(event_log_path, "a")

        def on_event(event):
            event_log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {event}\n")
            event_log.flush()

        for event in events:
            toplevel.bind(event, on_event)
