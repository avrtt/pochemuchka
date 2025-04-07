import json
import logging
import os
import time
from pytest import fixture
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv())
from pochemuchka import Pochemuchka, Prompt
logger = logging.getLogger(__name__)

@fixture
def pochemuchka_client():
    pochemuchka = Pochemuchka()
    return pochemuchka

def stream_function(text, **kwargs):
    print(text)

def stream_check_connection(validate, **kwargs):
    return validate

def test_openai_pricing(pochemuchka_client: Pochemuchka):

    context = {
        'ideal_answer': "There are eight planets",
        'text': "Hi! Please tell me how many planets are there in the solar system?"
    }

    prompt_id = f'unit-test_openai_pricing'
    pochemuchka_client.service.clear_cache()
    prompt = Prompt(id=prompt_id) 
    prompt.add("{text}", role='user')

    result_4o = pochemuchka_client.call(prompt.id, context, "openai/gpt-4o", test_data={'ideal_answer': "There are eight", 'behavior_name': "gemini"}, stream_function=stream_function, check_connection=stream_check_connection, params={"stream": True}, stream_params={"validate": True, "end": "", "flush": True})
    result_4o_mini = pochemuchka_client.call(prompt.id, context, "openai/gpt-4o-mini", test_data={'ideal_answer': "There are eight", 'behavior_name': "gemini"}, stream_function=stream_function, check_connection=stream_check_connection, params={"stream": True}, stream_params={"validate": True, "end": "", "flush": True})
    
    assert result_4o.metrics.price_of_call > 0
    assert result_4o_mini.metrics.price_of_call > 0
    
def test_claude_pricing(pochemuchka_client: Pochemuchka):

    context = {
        'ideal_answer': "There are eight planets",
        'text': "Hi! Please tell me how many planets are there in the solar system?"
    }

    prompt_id = f'test-{time.time()}'
    pochemuchka_client.service.clear_cache()
    prompt = Prompt(id=prompt_id) 
    prompt.add("{text}", role='user')
    
    result_haiku = pochemuchka_client.call(prompt.id, context, "claude/claude-3-5-haiku-latest", test_data={'ideal_answer': "There are eight", 'behavior_name': "gemini"}, stream_function=stream_function, check_connection=stream_check_connection, params={"stream": True}, stream_params={"validate": True, "end": "", "flush": True})
    result_sonnet = pochemuchka_client.call(prompt.id, context, "claude/claude-3-5-sonnet-latest", test_data={'ideal_answer': "There are eight", 'behavior_name': "gemini"}, stream_function=stream_function, check_connection=stream_check_connection, params={"stream": True}, stream_params={"validate": True, "end": "", "flush": True})
    
    assert result_sonnet.metrics.price_of_call > result_haiku.metrics.price_of_call