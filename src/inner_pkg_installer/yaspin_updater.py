import logging
from contextlib import contextmanager
from yaspin import yaspin


class YaspinLogUpdater:
    def __init__(self):
        self.text = None
        self.spinner = yaspin().runner

    def ok(self, ok_msg: str):
        self.spinner.ok(ok_msg)


@contextmanager
def yaspin_log_updater(msg, logger: logging.Logger):
    updater = YaspinLogUpdater()

    logger.info(msg)
    with updater.spinner as sp:
        sp.text = msg
        yield updater
        sp.ok("✅")
