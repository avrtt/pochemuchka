class PochemuchkaError(Exception):
    pass

class RetryableCustomError(PochemuchkaError):
    pass

class PochemuchkaPromptIsnotFoundError(PochemuchkaError):
    pass

class BehaviorIsNotDefined(PochemuchkaError):
    pass

class ConnectionLostError(PochemuchkaError):
    pass

class ValueIsNotResolvedError(PochemuchkaError):
    pass

class NotEnoughBudgetError(PochemuchkaError):
    pass

class NotFoundPromptError(PochemuchkaError):
    pass

class ProviderNotFoundError(PochemuchkaError):
    pass

class NotParsedResponseException(PochemuchkaError):
    pass

class APITokenNotProvided(PochemuchkaError):
    pass
