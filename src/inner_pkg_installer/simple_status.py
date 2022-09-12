import logging


def simple_status(
        base_logger: logging.Logger = logging.getLogger(""),
        std_out_logger: logging.Logger = logging.getLogger("")):
    def decorator(function):
        def wrapper(*args, **kwargs):
            std_out_logger.info(kwargs["status_msg_kwarg"])
            result = function(*args, **kwargs)
            return result
        return wrapper
    return decorator


