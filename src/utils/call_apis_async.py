import json

import aiohttp

from src.configurations.Types import Request_Method_Type

async def call_api(
    url,
    data=None,
    headers=None,
    text=False,
    timeout=None,
    method=Request_Method_Type.post,
):
    """
    Calling the openai api using an async post request
    Arguments:
    url: (text) url of the desired openai end-point
    data: (dict) request parameters

    Returns:
    json_response: (dict) response form the post request
    """
    
    headers = {"Content-Type": "application/json"} if not headers else headers
    """
    Total timeout for each request by default is 5 min. Making it 4 min. Note: This is only for one single api
    request initiated using httpio. This doesn't apply to overall timeout (i.e., time out for writer-service).
    """
    timeout = timeout or 60 * 1.5
    client_timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout, sock_read=timeout)
    async with aiohttp.ClientSession() as session:
        session = (
            session.post(url=url, json=data, headers=headers, timeout=client_timeout)
            if method == Request_Method_Type.post
            else session.get(url=url, json=data, headers=headers, timeout=client_timeout)
        )
        async with session as response:
            response_text = ""
            try:
                response_status_code = response.status
                response_text = await response.text()
                if text:
                    return response_text, response_status_code
                response_json = json.loads(response_text)
                return response_json, response_status_code
            except:
                return response_text, response_status_code
