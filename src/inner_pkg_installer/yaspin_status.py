import logging
from yaspin import yaspin


def yaspin_logging(
        base_logger: logging.Logger = logging.getLogger(""),
        std_out_logger: logging.Logger = logging.getLogger("")
):
    def decorator(function):
        def wrapper(*args, **kwargs):
            with yaspin().layer as spinner:
                spinner.text = kwargs["status_msg_kwarg"]
                base_logger.info(kwargs["status_msg_kwarg"])
                result = function(*args, **kwargs)
                spinner.ok("✔")
            return result
        return wrapper
    return decorator
