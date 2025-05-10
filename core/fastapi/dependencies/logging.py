from fastapi import BackgroundTasks


class Logging:
    """
    Class for handling background logging tasks.

    This class schedules a logging task to be executed in the background as part of the request's lifecycle.

    Args:
        background_task (BackgroundTasks): The background task manager, injected by FastAPI.
    """

    def __init__(self, background_task: BackgroundTasks):
        background_task.add_task(self._send_log)

    async def _send_log(self):
        """
        Placeholder method for sending log data in the background.

        This method should contain the logic for sending logs asynchronously.
        It will be executed in the background by FastAPI's background task system.
        """
        ...
