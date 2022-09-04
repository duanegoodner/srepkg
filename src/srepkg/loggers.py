import sys
from datetime import datetime
import logging
from pathlib import Path


class StreamLogger:
    def __init__(self, log_level):
        self._log_level = log_level
        self._buf = []

    def write(self, msg):
        if msg.endswith('\n'):
            self._buf.append(msg.removesuffix('\n'))
            self._log_level(''.join(self._buf))
            self._buf = []
        else:
            self._buf.append(msg)

    def flush(self):
        pass


class LoggingInitializer:

    def __init__(self, log_dir: Path):
        self._logfile_dir = log_dir
        self._logfile = (self._logfile_dir / datetime.now()
                         .strftime('%Y-%m-%d_%H_%M_%S_%f'))

    def setup_global_logger(self):

        self._logfile.touch(exist_ok=True)

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            filename=str(self._logfile),
            filemode='a'
        )

        console_gen = logging.StreamHandler()
        console_gen.setLevel(level=logging.WARNING)
        console_gen_formatter = logging.Formatter(
            '%(name)-12s: %(levelname)-8s %(message)s')
        console_gen.setFormatter(console_gen_formatter)
        gen_logger = logging.getLogger("gen_logger")
        gen_logger.addHandler(console_gen)

        # sys.stdout = StreamLogger(gen_logger.info)
        # sys.stderr = StreamLogger(gen_logger.error)




