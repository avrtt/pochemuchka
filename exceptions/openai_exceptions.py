from exceptions_general import PochemuchkaError, RetryableCustomError

class OpenAIChunkedEncodingError(RetryableCustomError):
    pass

class OpenAITimeoutError(RetryableCustomError):
    pass

class OpenAIResponseWasFilteredError(RetryableCustomError):
    pass

class OpenAIAuthenticationError(RetryableCustomError):
    pass

class OpenAIInternalError(RetryableCustomError):
    pass

class OpenAiRateLimitError(RetryableCustomError):
    pass

class OpenAiPermissionDeniedError(RetryableCustomError):
    pass

class OpenAIUnknownError(RetryableCustomError):
    pass

class OpenAIInvalidRequestError(PochemuchkaError):
    pass

class OpenAIBadRequestError(PochemuchkaError):
    pass

class ConnectionCheckError(PochemuchkaError):
    pass
