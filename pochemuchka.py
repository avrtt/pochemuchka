import logging
import typing as t
from dataclasses import dataclass
from decimal import Decimal
import requests
import time
import json
from settings import POCHEMUCHKA_API_URI
from pochemuchka import Secrets, settings    
from models import AI_MODELS_PROVIDER
from attempt_to_call import AttemptToCall
from behavior import AIModelsBehavior, PromptAttempts
from azure_models import AzureAIModel
from claude_model import ClaudeAIModel
from openai_models import OpenAIModel
from constants_general import C_16K
from exceptions_general import PochemuchkaPromptIsnotFoundError, RetryableCustomError
from save_worker import SaveWorker
from prompt_general import Prompt
from user_prompt import UserPrompt
from responses_general import AIResponse
from service_utils import PochemuchkaService
from utils_general import current_timestamp_ms

logger = logging.getLogger(__name__)

@dataclass
class Pochemuchka:
    api_token: str = None
    openai_key: str = None
    openai_org: str = None
    claude_key: str = None
    gemini_key: str = None
    azure_keys: t.Dict[str, str] = None
    nebius_key: str = None
    custom_key: str = None
    secrets: Secrets = None

    clients: dict = None

    def __post_init__(self):
        self.clients = {}
        self.secrets = Secrets()
        self._init_secrets()
        self._init_clients()
        self.worker = SaveWorker()
        self.service = PochemuchkaService()

    def _init_secrets(self):
        if not self.azure_keys and self.secrets.azure_keys:
            logger.debug("Using Azure keys from secrets")
            self.azure_keys = self.secrets.azure_keys
        elif not self.azure_keys:
            logger.debug("Azure keys not found in secrets")

        for attr, secret_attr in [
            ("api_token", "API_TOKEN"),
            ("openai_key", "OPENAI_API_KEY"),
            ("openai_org", "OPENAI_ORG"),
            ("gemini_key", "GEMINI_API_KEY"),
            ("claude_key", "CLAUDE_API_KEY"),
            ("nebius_key", "NEBIUS_API_KEY"),
            ("custom_key", "CUSTOM_API_KEY"),
        ]:
            if getattr(self, attr) is None and getattr(self.secrets, secret_attr, None):
                logger.debug(f"Using {secret_attr} from secrets")
                setattr(self, attr, getattr(self.secrets, secret_attr))

    def _init_clients(self):
        if self.openai_key:
            self.clients[AI_MODELS_PROVIDER.OPENAI] = {
                "organization": self.openai_org,
                "api_key": self.openai_key,
            }
        
        if self.azure_keys:
            self.clients.setdefault(AI_MODELS_PROVIDER.AZURE, {})
            for realm, key_data in self.azure_keys.items():
                self.clients[AI_MODELS_PROVIDER.AZURE][realm] = {
                    "api_version": key_data.get("api_version", "2023-07-01-preview"),
                    "azure_endpoint": key_data["url"],
                    "api_key": key_data["key"],
                }
                logger.debug(f"Initialized Azure client for {realm} {key_data['url']}")
            
        if self.claude_key:
            self.clients[AI_MODELS_PROVIDER.CLAUDE] = {"api_key": self.claude_key}
        if self.gemini_key:
            self.clients[AI_MODELS_PROVIDER.GEMINI] = {"api_key": self.gemini_key}
        if self.nebius_key:
            self.clients[AI_MODELS_PROVIDER.NEBIUS] = {"api_key": self.nebius_key}
        if self.custom_key:
            self.clients[AI_MODELS_PROVIDER.CUSTOM] = {"api_key": self.custom_key}

    def create_test(
        self,
        prompt_id: str,
        context: t.Dict[str, str],
        ideal_answer: str = None,
        model_name: str = None,
    ):
        url = f"{POCHEMUCHKA_API_URI}/lib/tests?createTest"
        headers = {"Authorization": f"Token {self.api_token}"}

        ideal_answer = context.get("ideal_answer", ideal_answer)

        data = {
            "prompt_id": prompt_id,
            "ideal_answer": ideal_answer,
            "model_name": model_name,
            "test_context": context,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(response)

    def extract_provider_name(self, model: str, provider_url: str = None) -> dict:
        parts = model.split("/")
        provider_lower = parts[0].lower()

        if provider_lower == "azure" and len(parts) == 3:
            _, realm, model_name = parts
            return {"provider": provider_lower, "model_name": model_name, "realm": realm, "base_url": None}
        elif provider_lower == "nebius" and len(parts) == 3:
            model_name = f"{parts[1]}/{parts[2]}"
            return {"provider": provider_lower, "model_name": model_name, "realm": None, "base_url": None}
        elif provider_lower == "custom":
            if len(parts) == 3:
                model_name = f"{parts[1]}/{parts[2]}"
            else:
                model_name = parts[1]
            return {"provider": provider_lower, "model_name": model_name, "realm": None, "base_url": provider_url}
        else:
            # фолбек для openai, gemini и т.д.
            model_name = parts[1] if len(parts) > 1 else ""
            return {"provider": provider_lower, "model_name": model_name, "realm": None, "base_url": None} 

    def init_attempt(self, model_info: dict) -> AttemptToCall:
        provider = model_info['provider']
        model_name = model_info['model_name']

        if provider in [
            AI_MODELS_PROVIDER.OPENAI.value,
            AI_MODELS_PROVIDER.GEMINI.value,
            AI_MODELS_PROVIDER.NEBIUS.value,
        ]:
            return AttemptToCall(
                ai_model=OpenAIModel(provider=AI_MODELS_PROVIDER(provider), model=model_name),
                weight=100,
            )
        elif provider == AI_MODELS_PROVIDER.CLAUDE.value:
            return AttemptToCall(
                ai_model=ClaudeAIModel(model=model_name),
                weight=100,
            )
        elif provider == AI_MODELS_PROVIDER.CUSTOM.value:
            return AttemptToCall(
                ai_model=OpenAIModel(model=model_name, provider=AI_MODELS_PROVIDER.CUSTOM, base_url=model_info['base_url']),
                weight=100,
            )
        else:
            return AttemptToCall(
                ai_model=AzureAIModel(realm=model_info['realm'], deployment_id=model_name),
                weight=100,
            )

    def init_behavior(self, model: str, provider_url: str = None) -> AIModelsBehavior:
        main_model_info = self.extract_provider_name(model, provider_url)
        main_attempt = self.init_attempt(main_model_info)

        fallback_attempts = [
            self.init_attempt(self.extract_provider_name(fb_model, provider_url))
            for fb_model in settings.FALLBACK_MODELS
        ]
        return AIModelsBehavior(attempt=main_attempt, fallback_attempts=fallback_attempts)

    def call(
        self,
        prompt_id: str,
        context: t.Dict[str, str],
        model: str,
        provider_url: str = None,
        params: t.Dict[str, t.Any] = {},
        version: str = None,
        count_of_retries: int = 5,
        test_data: dict = {},
        stream_function: t.Callable = None,
        check_connection: t.Callable = None,
        stream_params: dict = {},
    ) -> AIResponse:
        logger.debug(f"Calling {prompt_id}")
        start_time = current_timestamp_ms()
        prompt = self.get_prompt(prompt_id, version)

        behavior = self.init_behavior(model, provider_url)
        logger.info(behavior)

        prompt_attempts = PromptAttempts(behavior)

        while prompt_attempts.initialize_attempt():
            current_attempt = prompt_attempts.current_attempt
            user_prompt = prompt.create_prompt(current_attempt)
            calling_messages = user_prompt.resolve(context)

            for _ in range(count_of_retries):
                try:
                    result = current_attempt.ai_model.call(
                        calling_messages.get_messages(),
                        calling_messages.max_sample_budget,
                        stream_function=stream_function,
                        check_connection=check_connection,
                        stream_params=stream_params,
                        client_secrets=self.clients[current_attempt.ai_model.provider],
                        **params,
                    )
                    sample_budget = self.calculate_budget_for_text(user_prompt, result.get_message_str())
                    try:
                        result.metrics.price_of_call = self.get_price(
                            current_attempt, sample_budget, calling_messages.prompt_budget
                        )
                    except Exception as e:
                        logger.exception(f"Error while getting price: {e}")
                        result.metrics.price_of_call = 0

                    result.metrics.sample_tokens_used = sample_budget
                    result.metrics.prompt_tokens_used = calling_messages.prompt_budget
                    result.metrics.ai_model_details = current_attempt.ai_model.get_metrics_data()
                    result.metrics.latency = current_timestamp_ms() - start_time

                    if settings.USE_API_SERVICE and self.api_token:
                        timestamp = int(time.time() * 1000)
                        result.id = f"{prompt_id}#{timestamp}"
                        self.worker.add_task(
                            self.api_token,
                            prompt.service_dump(),
                            context,
                            result,
                            {**test_data, "call_model": model},
                        )
                    return result
                except RetryableCustomError as e:
                    logger.error(f"Attempt failed: {current_attempt} with retryable error: {e}")
                except Exception as e:
                    logger.error(f"Attempt failed: {current_attempt} with non-retryable error: {e}")

        logger.exception("Prompt call failed, no attempts worked")
        raise Exception("All attempts failed")

    def get_prompt(self, prompt_id: str, version: str = None) -> Prompt:
        logger.debug(f"Getting pipe prompt {prompt_id}")

        if settings.USE_API_SERVICE and self.api_token and settings.RECEIVE_PROMPT_FROM_SERVER:
            prompt_data = None
            prompt = settings.PIPE_PROMPTS.get(prompt_id)

            if prompt:
                prompt_data = prompt.service_dump()
            try:
                response = self.service.get_actual_prompt(self.api_token, prompt_id, prompt_data, version)

                if not response.is_taken_globally:
                    prompt.version = response.version
                    return prompt
                response.prompt["version"] = response.version

                return Prompt.service_load(response.prompt)
            
            except Exception as e:
                logger.exception(f"Error while getting prompt {prompt_id}: {e}")

                if prompt:
                    return prompt
                else:
                    logger.exception(f"Prompt {prompt_id} not found")
                    raise PochemuchkaPromptIsnotFoundError()
        else:
            return settings.PIPE_PROMPTS[prompt_id]

    def add_ideal_answer(self, response_id: str, ideal_answer: str):
        return PochemuchkaService.update_response_ideal_answer(self.api_token, response_id, ideal_answer)

    def calculate_budget_for_text(self, user_prompt: UserPrompt, text: str) -> int:
        if not text:
            return 0
        return len(user_prompt.encoding.encode(text))

    def get_price(self, attempt: AttemptToCall, sample_budget: int, prompt_budget: int) -> Decimal:
        data = {
            "provider": attempt.ai_model.provider.value,
            "model": attempt.ai_model.name,
            "output_tokens": sample_budget,
            "input_tokens": prompt_budget,
        }

        response = requests.post(f"{POCHEMUCHKA_API_URI}/lib/pricing", data=json.dumps(data))
        if response.status_code != 200:
            return 0
        return response.json().get("price", 0)
