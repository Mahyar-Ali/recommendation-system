from src.utils.call_apis_async import call_api
from json import JSONDecodeError
from src.config import openai_api


# This file contains class for inappropriate content error.
class InappropriateContentError(Exception):
    pass


async def call_filter_openai_api(response_from_model, userIdentifier=""):
    """
    This function calls the openai api given a prompt for text generation.
    parameters :
        (1) response_from_model {str} : The textual output from the model
    """
    assert response_from_model != None, f"\n\nNone response recieved\n\n"
    data = {
        "prompt": "<|endoftext|>" + response_from_model + "\n--\nLabel:",
        "temperature": 0,
        "max_tokens": 1,
        "top_p": 1,
        "logprobs": 10,
    }
    engine = "content-filter-alpha"

    if userIdentifier:
        data["user"] = userIdentifier

    url = f"https://api.openai.com/v1/engines/{engine}/completions"

    headers =  {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api}",
    }

    response, response_status_code = await call_api(url, data, headers=headers,timeout=5)
    if response_status_code != 200:
        raise JSONDecodeError("JSONDecodeError", response)
    # output_label = replace_characters(json_response["choices"][0]["text"])

    output_label = response["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

    # if the most probable token is none of "0", "1", or "2"
    # this should be set as unsafe
    if output_label not in ["0", "1", "2"]:
        output_label = "2"
    return output_label


async def check_for_inappropriate_content(text, userIdentifier=""):
    """
    This functions checks if the text contains any inappropriate content
    """
    label = ""
    try:
        label = await call_filter_openai_api(
            response_from_model=text, userIdentifier=userIdentifier
        )
    except Exception as e:
        pass
    if label == "2":
        return {"inappropriate":True}
    else:
        return {"inappropriate":False}
