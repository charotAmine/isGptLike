from semantic_kernel.skill_definition import (
    sk_function,
    sk_function_context_parameter,
)
from semantic_kernel.orchestration.sk_context import SKContext


class Weather:
    @sk_function(
        description="Returns the weather",
        name="define_weather",
        input_description="which city",
    )    
    def define_weather(self) -> str:
        return "30° in braziu"
