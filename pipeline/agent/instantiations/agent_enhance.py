from pipeline.agent.agent import Agent
from pipeline.config.config import config
from dotenv import load_dotenv
import os


system_message = """
You are a helpful assistant, you will get a question and you are to rephrase the question in 200 different ways.
Use different wording (if possible).
Try to use unique words as much as possible.

Constraints:
You should only respond in JSON format as described below Response Format: {"questions": [list of questions]}
Ensure the response can be parsed by Python json.loads
"""
enhance_question = Agent("ENHANCE_QUESTION",
    ai=config.ai, system_prompt=system_message, commands=[], format={"questions": "[list of questions]"})


