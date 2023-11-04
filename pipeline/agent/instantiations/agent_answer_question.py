from pipeline.agent.agent import Agent
from pipeline.config.config import config

system_message = """
You are an consultant in the area of international cooperation. 
You will get a text and a question.
If answer exist in text - answer according to the text.
If not - flag.

Commands:
answer: "answer the question based on the information in the text"
flag: "Can't answer", args: "reasoning": "<why you can not make a decision>"

You should only respond in JSON format as described below Response Format: { "thoughts": { "reasoning": "reasoning", "criticism": "constructive self-criticism", "speak": "thoughts summary" }, "command": { "name": "command name", "args": { "arg name": "value" } }, "answer": "answer based on the provided text" }
Ensure the response can be parsed by Python json.loads
    """


def gen_prompt(data):
    question = data.get("question")
    text = data.get("text")
    return f"""
text:
{text}    

question: {question}
    """


format = { "thoughts": { "reasoning": "reasoning", "criticism": "constructive self-criticism", "speak": "thoughts summary" }, "command": { "name": "command name", "args": { "arg name": "value" } }, "answer": "answer based on the provided text" }
answer_agent = Agent("answer_agent",
                     ai=config.ai, system_prompt=system_message, commands=[], format=format, prompt_generator=gen_prompt)


