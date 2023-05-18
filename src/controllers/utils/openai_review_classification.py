prompt = [
    {
        "role": "system",
        "content": "TASK: You will be given the review written by a random user and you will have to classify the review between 1-5. Just write the numerical review in response"
    },
    {
        "role":"user",
        "content": "Review: {REVIEW_TEXT}"
    }
]
data = {
    "model": "gpt-3.5-turbo",
    "messages": "",
    "temperature": 0.7,
    "max_tokens": 10,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": ['###'],
}