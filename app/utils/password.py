import base64
class Password(str):

    def encode(str):
        return base64.b64encode(str.encode("utf-8")).decode("utf-8")

    def decode(str):
        return base64.b64decode(str).decode("utf-8")

