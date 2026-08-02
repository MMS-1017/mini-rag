from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CohereProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create_provider(self, provider_name: str):
        if provider_name == LLMEnums.OPENAI.value :
            return OpenAIProvider(
                api_key=self.config.get("OPENAI_API_KEY"),
                api_url=self.config.get("OPENAI_API_URL"),
                default_input_max_characters=self.config.get("INPUT_DEFAULT_MAX_CHARACTERS", 1000),
                default_generation_max_output_tokens=self.config.get("GENERATION_DEFAULT_MAX_CHARACTERS", 200),
                default_generation_temperature=self.config.get("GENERATION_DEFAULT_MAX_TEMPERATURE", 0.1)
            )
        
        elif provider_name == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key=self.config.get("COHERE_API_KEY"),
                default_input_max_characters=self.config.get("INPUT_DEFAULT_MAX_CHARACTERS", 1000),
                default_generation_max_output_tokens=self.config.get("GENERATION_DEFAULT_MAX_CHARACTERS", 200),
                default_generation_temperature=self.config.get("GENERATION_DEFAULT_MAX_TEMPERATURE", 0.1)
            )
        else:
            return None