import json
import logging
import typing as t
from dataclasses import asdict, dataclass
import requests
from pochemuchka import settings
from exceptions_general import NotFoundPromptError
from responses_general import AIResponse
from utils_general import DecimalEncoder, current_timestamp_ms

logger = logging.getLogger(__name__)

@dataclass
class PochemuchkaServiceResponse:
    prompt_id: str = None
    prompt: dict = None
    is_taken_globally: bool = False
    version: str = None

class PochemuchkaService:
    url: str = settings.POCHEMUCHKA_API_URI
    cached_prompts = {}

    def get_actual_prompt(
        self,
        api_token: str,
        prompt_id: str,
        prompt_data: dict = None,
        version: str = None,
    ) -> PochemuchkaServiceResponse:
        logger.debug(
            f"Received request to get actual prompt prompt_id: {prompt_id}, prompt_data: {prompt_data}, version: {version}"
        )
        timestamp = current_timestamp_ms()
        logger.debug(f"Getting actual prompt for {prompt_id}")
        cached_prompt = None
        cached_prompt_taken_globally = False
        cached_data = self.get_cached_prompt(prompt_id)

        if cached_data:
            cached_prompt = cached_data.get("prompt")
            cached_prompt_taken_globally = cached_data.get("is_taken_globally")
            
            if cached_prompt:
                logger.debug(
                    f"Prompt {prompt_id} is cached, returned in {current_timestamp_ms() - timestamp} ms"
                )
                return PochemuchkaServiceResponse(
                    prompt_id=prompt_id,
                    prompt=cached_prompt,
                    is_taken_globally=cached_prompt_taken_globally,
                )

        url = f"{self.url}/lib/prompts"

        headers = {
            "Authorization": f"Token {api_token}",
        }

        data = {
            "prompt": prompt_data,
            "id": prompt_id,
            "version": version,
            "is_taken_globally": cached_prompt_taken_globally,
        }

        json_data = json.dumps(data, cls=DecimalEncoder)
        response = requests.post(url, headers=headers, data=json_data)

        if response.status_code == 200:
            response_data = response.json()
            logger.debug(
                f"Prompt {prompt_id} found in {current_timestamp_ms() - timestamp} ms: {response_data}"
            )
            prompt_data = response_data.get("prompt", prompt_data)
            is_taken_globally = response_data.get("is_taken_globally")
            version = response_data.get("version")

            self.cached_prompts[prompt_id] = {
                "prompt": prompt_data,
                "timestamp": current_timestamp_ms(),
                "is_taken_globally": is_taken_globally,
                "version": version,
            }

            return PochemuchkaServiceResponse(
                prompt_id=prompt_id,
                prompt=prompt_data,
                is_taken_globally=response_data.get("is_taken_globally", False),
                version=version,
            )
        else:
            logger.debug(
                f"Prompt {prompt_id} not found, in {current_timestamp_ms() - timestamp} ms"
            )

            raise NotFoundPromptError(response.json())

    def get_cached_prompt(self, prompt_id: str) -> dict:
        cached_data = self.cached_prompts.get(prompt_id)

        if not cached_data:
            return None

        cached_delay = current_timestamp_ms() - cached_data.get("timestamp")
        if cached_delay < settings.CACHE_PROMPT_FOR_EACH_SECONDS * 1000:
            return cached_data
        
        return None

    @classmethod
    def clear_cache(cls):
        cls.cached_prompts = {}

    @classmethod
    def save_user_interaction(
        cls,
        api_token: str,
        prompt_data: t.Dict[str, t.Any],
        context: t.Dict[str, t.Any],
        response: AIResponse,
    ):
        url = f"{cls.url}/lib/logs"
        headers = {"Authorization": f"Token {api_token}"}
        data = {
            "context": context,
            "prompt": prompt_data,
            "response": {"content": response.content},
            "metrics": asdict(response.metrics),
            "request": asdict(response.prompt),
            "timestamp": response.id.split("#")[1],
        }

        logger.debug(f"Request to {url} with data: {data}")
        json_data = json.dumps(data, cls=DecimalEncoder)

        response = requests.post(url, headers=headers, data=json_data)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(response)

    @classmethod
    def update_response_ideal_answer(
        cls, api_token: str, log_id: str, ideal_answer: str
    ):
        url = f"{cls.url}/lib/logs"
        headers = {"Authorization": f"Token {api_token}"}
        data = {"log_id": log_id, "ideal_answer": ideal_answer}

        logger.debug(f"Request to {url} with data: {data}")
        json_data = json.dumps(data, cls=DecimalEncoder)

        response = requests.put(url, headers=headers, data=json_data)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(response)
            return response

    @classmethod
    def create_test_with_ideal_answer(
        cls,
        api_token: str,
        prompt_data: t.Dict[str, t.Any],
        context: t.Dict[str, t.Any],
        test_data: dict,
    ):
        ideal_answer = test_data.get("ideal_answer", None)

        if not ideal_answer:
            return
        
        url = f"{cls.url}/lib/tests"
        headers = {"Authorization": f"Token {api_token}"}
        model_name = test_data.get("model_name") or test_data.get("call_model") or None

        data = {
            "context": context,
            "prompt": prompt_data,
            "ideal_answer": ideal_answer,
            "model_name": model_name,
        }

        logger.debug(f"Request to {url} with data: {data}")
        json_data = json.dumps(data)
        requests.post(url, headers=headers, data=json_data)
        logger.info(f"Created CI/CD for prompt {prompt_data['prompt_id']}")
