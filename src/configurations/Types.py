from enum import Enum


class Request_Method_Type(str, Enum):
    get = "get"
    post = "post"