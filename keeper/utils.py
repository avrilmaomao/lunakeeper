import concurrent.futures
import hashlib
import logging
from urllib import request
import json
from concurrent.futures import ThreadPoolExecutor


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def send_json_request(url: str, params: dict, ret_json=True) -> dict:
    post_data = json.dumps(params).encode('utf-8')
    req = request.Request(url, data=post_data, headers= {'content-type': 'application/json'})
    response = request.urlopen(req)
    response_text = response.read().decode('utf-8')
    if ret_json:
        return json.loads(response_text)
    return response_text


def run_in_background(func , *args, **kwargs) -> concurrent.futures.Future:
    f = run_in_background.executor.submit(func,*args, **kwargs)
    return f


run_in_background.executor = ThreadPoolExecutor(max_workers=3)
logging.info("utils imported")