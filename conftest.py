import pytest
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv())
from models import behavior
from attempt_to_call import AttemptToCall
from azure_models import AzureAIModel
from openai_models import C_128K, C_32K, OpenAIModel
from openai.types.chat.chat_completion import ChatCompletion
from pochemuchka import Pochemuchka
from prompt_general import Prompt
import logging

@pytest.fixture(autouse=True)
def set_log_level():
    logging.getLogger().setLevel(logging.DEBUG)

@pytest.fixture
def pochemuchka():
    return Pochemuchka(
        openai_key="123",
        azure_keys={"us-east-1": {"url": "https://us-east-1.api.azure.openai.org", "key": "123"}}
    )

@pytest.fixture
def openai_gpt_4_behavior():
    return behavior.AIModelsBehavior(
        attempts=[
            AttemptToCall(
                ai_model=OpenAIModel(
                    model="gpt-4-1106-preview",
                    max_tokens=C_128K,
                    support_functions=True,
                ),
                weight=100,
            ),
        ]
    )

@pytest.fixture
def azure_gpt_4_behavior():
    return behavior.AIModelsBehavior(
        attempts=[
            AttemptToCall(
                ai_model=AzureAIModel(
                    realm='useast',
                    deployment_id="gpt-4o",
                    max_tokens=C_128K,
                    support_functions=True,
                ),
                weight=100,
            ),
        ]
    )

@pytest.fixture
def gpt_4_behavior():
    return behavior.AIModelsBehavior(
        attempts=[
            AttemptToCall(
                ai_model=AzureAIModel(
                    realm='useast',
                    deployment_id='gpt-4o',
                    max_tokens=C_128K,
                ),
                weight=1,
            ),
            AttemptToCall(
                ai_model=OpenAIModel(
                    model="gpt-4-1106-preview",
                    max_tokens=C_128K,
                    support_functions=True,
                ),
                weight=100,
            ),
        ],
        fallback_attempt=AttemptToCall(
            ai_model=AzureAIModel(
                realm="useast",
                deployment_id="gpt-4o",
                max_tokens=C_32K,
                support_functions=True,
            ),
            weight=1,
        ),
    )

@pytest.fixture
def hello_world_prompt():
    prompt = Prompt(id='hello-world')
    prompt.add("<ADD PROMPT HERE>")
    prompt.add("""<ADD PROMPT HERE>""", role='assistant')
    prompt.add("""<ADD PROMPT HERE>""")
    return prompt
    
@pytest.fixture
def chat_completion_openai():
    return ChatCompletion(
        **{
            "id": "id",
            "choices": [
                {
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": "Hey you!",
                        "role": "assistant",
                        "function_call": None,
                    },
                    "logprobs": None,
                }
            ],
            "created": 42,
            "model": "gpt-4",
            "object": "chat.completion",
            "system_fingerprint": "fingerprinto",
            "usage": {
                "completion_tokens": 10,
                "prompt_tokens": 20,
                "total_tokens": 30,
            },
        }
    )