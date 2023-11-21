import json
from typing import Dict
from pipeline.agent.instantiations.magic_assistant import magic_assistant
from pipeline.shared_content import logger



def loadString(text: str, format: Dict[str, str] = None, attemps: int = 3) -> Dict[str, str]:
    """
    This function parse the LLM response and return a JSON.
    Exapmles: https://github.com/Kruvxyz/Auto-GPT/blob/stable/autogpt/json_utils/json_fix_llm.py (fix_json_using_multiple_techniques)
    """
    text_to_parse = text
    for i in range(attemps):
        logger.info(f"attemp {i} to parse {text}")
        decoration_init = text_to_parse.find("```json")
        decoration_end = text_to_parse.find("```", decoration_init + 7)
        if decoration_init>-1 and decoration_end>-1:
            logger.info(f"clean up text to parse from {text_to_parse} to {text_to_parse[decoration_init+7:decoration_end]}")
            text_to_parse = text_to_parse[decoration_init+7:decoration_end]

        try:
            parsed_response = json.loads(text_to_parse, strict=False)
            return parsed_response

        except:
            user_input = f"Convert this text: \n{text},\n\n to a Json file. say nothing except for json. use this format:\n '''{json.dumps(format, indent=2)}'''\nEnsure the response can be parsed by Python json.loads"
            text_to_parse = magic_assistant.talk(user_input=user_input, format=format)
    raise SyntaxError(f"Could not parse response to expected format {format}", (
        "ParseToJson.py", 20, 11, f"failed to parse string: {text}"))
