import logging
from time import sleep
from datetime import datetime as dt
import dotenv
dotenv.load_dotenv()
from pytest import fixture
from pochemuchka import Pochemuchka, behavior, Prompt, AttemptToCall, AzureAIModel, C_128K
logger = logging.getLogger(__name__)

@fixture
def client():
    import dotenv
    dotenv.load_dotenv(dotenv.find_dotenv())
    pochemuchka = Pochemuchka()
    return pochemuchka

def test_loading_prompt_from_service(client: Pochemuchka):

    context = {
        'messages': ['test1', 'test2'],
        'assistant_response_in_progress': None,
        'files': ['file1', 'file2'],
        'music': ['music1', 'music2'],
        'videos': ['video1', 'video2'],
    }

    prompt_id = f'unit-test-loading_prompt_from_service'
    client.service.clear_cache()
    prompt = Prompt(id=prompt_id, max_tokens=10000)
    first_str_dt = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    prompt.add(f"It's a system message, Hello at {first_str_dt}", role="system")
    prompt.add('{messages}', is_multiple=True, in_one_message=True, label='messages')
    print(client.call(prompt.id, context, "azure/useast/gpt-4o"))

    client.service.clear_cache()
    prompt = Prompt(id=prompt_id, max_tokens=10000)
    next_str_dt = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    prompt.add(f"It's a system message, Hello at {next_str_dt}", role="system")
    prompt.add('{music}', is_multiple=True, in_one_message=True, label='music')
    print(client.call(prompt.id, context, "azure/useast/gpt-4o"))

    sleep(2)
    client.service.clear_cache()
    prompt = Prompt(id=prompt_id, max_tokens=10000)
    prompt.add(f"It's a system message, Hello at {first_str_dt}", role="system")
    prompt.add('{messages}', is_multiple=True, in_one_message=True, label='messages')
    result = client.call(prompt.id, context, "azure/useast/gpt-4o")
    
    assert result.prompt.messages[-1] == {'role': 'user', 'content': 'music1\nmusic2'} 
