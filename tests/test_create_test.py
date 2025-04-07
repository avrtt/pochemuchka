import logging
import os
import time
from pytest import fixture
from pochemuchka import Pochemuchka, Prompt
logger = logging.getLogger(__name__)

@fixture
def client():
    api_token = os.getenv("POCHEMUCHKA_API_TOKEN")
    pochemuchka = Pochemuchka(api_token=api_token)
    return pochemuchka

def test_creating_pochemuchka_test(client):
    
    context = {
        'ideal_answer': "There are eight planets",
        'text': "Hi! Please tell me how many planets are there in the solar system?"
    }

    prompt_id = f'unit-test-creating_fp_test'
    client.service.clear_cache()
    prompt = Prompt(id=prompt_id) 
    prompt.add("{text}", role='user')

    client.create_test(prompt_id, context, model_name="gemini/gemini-1.5-flash")