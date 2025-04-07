import logging
import random
import typing as t
from copy import copy
from dataclasses import dataclass
from attempt_to_call import AttemptToCall
from exceptions_general import BehaviorIsNotDefined

logger = logging.getLogger(__name__)

@dataclass
class AIModelsBehavior:
    attempt: AttemptToCall
    fallback_attempts: list[AttemptToCall] = None

@dataclass
class PromptAttempts:
    ai_models_behavior: AIModelsBehavior
    current_attempt: AttemptToCall = None

    def initialize_attempt(self):
        if self.current_attempt is None:
            self.current_attempt = self.ai_models_behavior.attempt
            self.fallback_index = 0
            return self.current_attempt
        elif self.ai_models_behavior.fallback_attempts:
            if self.fallback_index < len(self.ai_models_behavior.fallback_attempts):
                self.current_attempt = self.ai_models_behavior.fallback_attempts[self.fallback_index]
                self.fallback_index += 1
                return self.current_attempt
            else:
                self.current_attempt = None
                return None

    def __str__(self) -> str:
        return f"Current attempt {self.current_attempt} from {len(self.ai_models_behavior.attempts)}"
