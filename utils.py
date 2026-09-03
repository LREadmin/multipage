""" Contains utility functions
"""
import subprocess
import traceback
import json
import sys

def error_logger(
        channel_name='test',
        alert_script_path='/home/cron/bin/post_to_chat.sh'
    ):
    """ Input:
            channel_name: str - the name of the teams channel we want to post
                an alert to. This has to be a valid option for the script
                we have set up to post messages to our Teams alerts channel
            alert_script_path: str - the path to the alert script.
        Output:
            func: function

    This is a decorator that will wrap a function. On failure, the error is
    caught and a message is sent to our Teams channel.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                x = '\n'.join([i for i in traceback.format_exception(
                    exc_type, exc_value, exc_traceback)])
                msg = json.dumps(x).strip('"')
                subprocess.run(
                    [
                        'bash',
                        alert_script_path,
                        f'--{channel_name}',
                        f"{msg}"
                    ],
                    check=False
                )
        return wrapper
    return decorator
