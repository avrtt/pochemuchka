import logging
from pytest import fixture
from pochemuchka import Pochemuchka, Prompt
logger = logging.getLogger(__name__)

@fixture
def client():
    import dotenv
    dotenv.load_dotenv(dotenv.find_dotenv())
    pochemuchka = Pochemuchka()
    return pochemuchka

def stream_function(text, **kwargs):
    print(text)

def stream_check_connection(validate, **kwargs):
    return validate

def test_creating_pochemuchka_test(client):

    context = {
        'ideal_answer': "There are eight planets",
        'text': "Hi! Please tell me how many planets are there in the solar system?"
    }

    prompt_id = f'unit-test-creating_fp_test'
    client.service.clear_cache()
    prompt = Prompt(id=prompt_id) 
    prompt.add("{text}", role='user')

    client.call(prompt.id, context, "azure/useast/gpt-4o", test_data={'ideal_answer': "There are eight", 'model_name': "gemini/gemini-1.5-flash"}, stream_function=stream_function, check_connection=stream_check_connection, params={"stream": True}, stream_params={"validate": True, "end": "", "flush": True})