"""LLM config placeholder."""
from langchain_openai import ChatOpenAI

from ..constants.openai_constants import OpenaiModels
from ..utils.logger import get_logger

logger = get_logger()


class LLMConfig:
    """LLM configuration class.
    Usage: 
        llm_config = LLMConfig(OpenaiModels.GPT_4_1.value, temperature=0.2)
        llm = llm_config.get_llm_instance()
    
    """

    def __init__(self, model_name: str = OpenaiModels.GPT_4_1.value, temperature: float = 0.2):
        self.model_name = model_name
        self.temperature = temperature
    
    def get_llm_instance(self) -> ChatOpenAI:
        """Returns an instance of ChatOpenAI with the specified configuration."""
        logger.info(
            "OpenAI client initialised with model '%s' and temperature %.2f",
            self.model_name,
            self.temperature,
        )
        return ChatOpenAI(model_name=self.model_name, temperature=self.temperature)