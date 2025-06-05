import json
import logging
import os
import subprocess
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI

from src.utils.client import completions_client
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
def setup_logger(name, log_file='./run.log', level=logging.INFO, log_to_file=False):
    """Function to set up a logger with a specific name and log file."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s')

    # Changed to use stderr instead of stdout
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    # Create a logger and set its level
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Prevent propagation to parent loggers
    logger.propagate = False
        
    logger.addHandler(handler)

    return logger

common_logger = setup_logger('logger')
logger = common_logger

def read_json_from_file(file_name):
    logger.info(f"Reading json from {file_name}")
    try:
        with open(file_name, 'r') as file: 
            out = file.read()
            out = json.loads(out)
            return out
    except Exception as e:
        logger.error(e)
        return None

def get_api_key(key_name):
    api_key = os.getenv(key_name)
    # Check if the API key was loaded successfully
    if not api_key:
        raise ValueError(f"{key_name} not found. Did you set it in the .env file?")
    return api_key

def generate_gpt4o_output_from_multi_turn_conv(messages, output_type='json', model="gpt-4o"):
    return generate_openai_output(messages, output_type, model)

def generate_openai_output(messages, output_type='not_json', model="gpt-4o", return_completion=False):
    print(f"In generate_openai_output, using client: {completions_client} and model: {model}")
    try:
        if output_type == 'json':
            chat_completion = completions_client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
        else:
            chat_completion = completions_client.chat.completions.create(
                model=model,
                messages=messages,
            )
        
        if return_completion:
            return chat_completion
        return chat_completion.choices[0].message.content

    except Exception as e:
        logger.error(e)
        return None

def generate_gemini_output(messages, output_type='not_json', model="gemini-1.5-pro"):
    if not GEMINI_AVAILABLE:
        raise ValueError("Google Generative AI package not available. Install with: pip install google-generativeai")
    
    try:
        # Configure the Gemini client
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file")
        
        genai.configure(api_key=gemini_api_key)
        
        # Convert OpenAI-style messages to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                # Gemini doesn't have a system role, so we'll prepend it to the first user message
                continue
            elif msg['role'] == 'user':
                gemini_messages.append({
                    'role': 'user',
                    'parts': [msg['content']]
                })
            elif msg['role'] == 'assistant':
                gemini_messages.append({
                    'role': 'model',
                    'parts': [msg['content']]
                })
        
        # Add system message to the first user message if present
        system_content = ""
        for msg in messages:
            if msg['role'] == 'system':
                system_content = msg['content']
                break
        
        if system_content and gemini_messages and gemini_messages[0]['role'] == 'user':
            gemini_messages[0]['parts'][0] = f"System: {system_content}\n\nUser: {gemini_messages[0]['parts'][0]}"
        
        # Create the model
        generation_config = {}
        if output_type == 'json':
            generation_config['response_mime_type'] = 'application/json'
        
        gemini_model = genai.GenerativeModel(model_name=model, generation_config=generation_config)
        
        # Generate response
        response = gemini_model.generate_content(gemini_messages)
        return response.text

    except Exception as e:
        logger.error(e)
        return None

def generate_anthropic_output(messages, output_type='not_json', model="claude-3-5-sonnet-20241022"):
    if not ANTHROPIC_AVAILABLE:
        raise ValueError("Anthropic package not available. Install with: pip install anthropic")
    
    try:
        # Configure the Anthropic client
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please set it in your .env file")
        
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Extract system message if present
        system_message = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                anthropic_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Create the completion
        kwargs = {
            'model': model,
            'max_tokens': 4096,
            'messages': anthropic_messages
        }
        
        if system_message:
            kwargs['system'] = system_message
        
        response = client.messages.create(**kwargs)
        return response.content[0].text

    except Exception as e:
        logger.error(e)
        return None

def generate_llm_output(messages, model):
    model_provider = None
    if "gpt" in model:
        model_provider = "openai"
    elif "gemini" in model:
        model_provider = "gemini"
    elif "claude" in model:
        model_provider = "anthropic"
    else:
        raise ValueError(f"Model {model} not supported")

    if model_provider == "openai":
        response = generate_openai_output(messages, output_type='text', model=model)
        return response
    elif model_provider == "gemini":
        response = generate_gemini_output(messages, output_type='text', model=model)
        return response
    elif model_provider == "anthropic":
        response = generate_anthropic_output(messages, output_type='text', model=model)
        return response
    
def generate_gpt4o_output_from_multi_turn_conv_multithreaded(messages, retries=5, delay=1, output_type='json'):
    while retries > 0:
        try:
            # Call GPT-4o API
            output = generate_gpt4o_output_from_multi_turn_conv(messages, output_type='json')
            return output  # If the request is successful, break out of the loop
        except openai.RateLimitError:
            print(f'Rate limit exceeded. Retrying in {delay} seconds...')
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            retries -= 1

    if retries == 0:
        print(f'Failed to process due to rate limit.')
        return []

def convert_message_content_json_to_strings(messages):
    for msg in messages:
        if 'content' in msg.keys() and isinstance(msg['content'], dict):
            msg['content'] = json.dumps(msg['content'])
    return messages

def merge_defaultdicts(dict_parent, dict_child):
    for key, value in dict_child.items():
        if key in dict_parent:
            # If the key exists in both, handle merging based on type
            if isinstance(dict_parent[key], list):
                dict_parent[key].extend(value)
            elif isinstance(dict_parent[key], dict):
                dict_parent[key].update(value)
            elif isinstance(dict_parent[key], set):
                dict_parent[key].update(value)
            else:
                dict_parent[key] += value  # For other types like int, float, etc.
        else:
            dict_parent[key] = value
    
    return dict_parent

def read_jsonl_from_file(file_name):
    # logger.info(f"Reading jsonl from {file_name}")
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            dataset = [json.loads(line.strip()) for line in lines]
        return dataset
    except Exception as e:
        logger.error(e)
        return None

def write_jsonl_to_file(list_dicts, file_name):
    try:
        with open(file_name, 'w') as file:
            for d in list_dicts:
                file.write(json.dumps(d)+'\n')
        return True
    except Exception as e:
        logger.error(e)
        return False

def read_text_from_file(file_name):
    try:
        with open(file_name, 'r') as file: 
            out = file.read()
        return out
    except Exception as e:
        logger.error(e)
        return None
    
def write_json_to_file(data, file_name):
    try:
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        logger.error(e)
        return False


def get_git_path(path):
    # Run `git rev-parse --show-toplevel` to get the root of the Git repository
    try:
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return f"{git_root}/{path}"
    except subprocess.CalledProcessError:
        raise RuntimeError("Not inside a Git repository")

def update_tokens_used(provider, model, tokens_used, completion):
    provider_model = f"{provider}/{model}"
    input_tokens = completion.usage.prompt_tokens
    output_tokens = completion.usage.completion_tokens
    
    if provider_model not in tokens_used:   
        tokens_used[provider_model] = {
            'input_tokens': 0,
            'output_tokens': 0,
        }
    
    tokens_used[provider_model]['input_tokens'] += input_tokens
    tokens_used[provider_model]['output_tokens'] += output_tokens
    
    return tokens_used