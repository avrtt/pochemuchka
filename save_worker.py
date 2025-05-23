import threading
import queue
import typing as t
from time import sleep
from responses_general import AIResponse
from service_utils import PochemuchkaService

class SaveWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def save_user_interaction_async(
        self,
        api_token: str,
        prompt_data: t.Dict[str, t.Any],
        context: t.Dict[str, t.Any],
        response: AIResponse,
    ):
        PochemuchkaService.save_user_interaction(
            api_token, prompt_data, context, response
        )

    def worker(self):
        while True:
            task = self.queue.get()

            if task is None:
                sleep(1)
                continue
            
            api_token, prompt_data, context, response, test_data = task
            PochemuchkaService.save_user_interaction(
                api_token, prompt_data, context, response
            )
            PochemuchkaService.create_test_with_ideal_answer(
                api_token, prompt_data, context, test_data
            )
            self.queue.task_done()

    def add_task(
        self,
        api_token: str,
        prompt_data: t.Dict[str, t.Any],
        context: t.Dict[str, t.Any],
        response: AIResponse,
        test_data: t.Optional[dict] = None,
    ):
        self.queue.put((api_token, prompt_data, context, response, test_data))
