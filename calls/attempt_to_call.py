import typing as t
from dataclasses import dataclass
from models import AIModel

@dataclass
class AttemptToCall:
    ai_model: AIModel
    weight: int = 1
    functions: t.List[str] = None
    attempt_number: int = 1

    def __post_init__(self):
        self.id = (
            f"{self.ai_model.name}"
            f"-n{self.attempt_number}-"
            f"{self.ai_model.provider.value}"
        )

    def __str__(self) -> str:
        return self.id

    def params(self) -> t.Dict[str, t.Any]:
        self.ai_model.get_params()

    def get_functions(self) -> t.List[str]:
        if not self.ai_model.support_functions:
            return []
        if self.functions is None:
            return None
        return self.functions

    def model_max_tokens(self) -> int:
        return self.ai_model.max_tokens

    def tiktoken_encoding(self) -> str:
        return self.ai_model.tiktoken_encoding
