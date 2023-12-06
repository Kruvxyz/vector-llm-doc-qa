from pipeline.flows.abstract.generic_flow import AbstractFlow
from typing import Any, Callable, Dict, List, Optional, Tuple
from pipeline.shared_content import shared, logger
from pipeline.functions.ParsePdf import load_page_from_doc
from app.functions.db import create_connection, update_answer
from db import db_path

db_file = db_path # f'{db_path}/mysql/database.db'

# class AnswerPdf(AbstractFlow):
#   def __init__(self,
#                config: "Config",
#                agents: Dict[str, "Agent"],
#                id: str,
#     ) -> None:
#     super().__init__(config)
#     self.agents = agents
#     self.current_agent = self.agents.get("init", None)
#     self.id = id
#     assert type(self.current_agent) != type(None), "Failed to load initial agent"

#     self.input = {"question": "", "text": ""}
#     self.mem = ""
#     self.state: str = self.config.STATE_NONE
#     self.set_agent_dict()
#     self.data = None

#   def pre_execute_loop(self, content: str) -> None:
#     """
#     Update self params befor executing loop
#     """
#     self.input["question"] = content
#     self.current_agent = self.agents["init"]
#     self.prepare()

#   def prepare(self) -> None:
#     self.state = self.config.STATE_RUN
#     if self.data is None:
#       self.data = shared.get_response(self.id)["answer"]

#     if self.data[0]["valid"] is not None:
#       self.state = self.config.STATE_CONTINUE

#     doc_path = self.data[0]["document"]
#     page = self.data[0]["page"]
#     self.input["text"] = load_page_from_doc(doc_path, page)

#   def execute(self, data: Dict[str,Any]) -> None:
#     """
#     Execute command
#     """
#     command_name, args = self.parse_command(data)
#     command = command_name.upper()

#     response = self.data[0]
#     valid=False
#     document = response["document"]
#     page = response["page"]
#     score = response["score"]
#     answer = None

#     if command == self.config.COMMAND_ANSWER:
#       self.state = self.config.STATE_CONTINUE
#       answer = data["answer"]
#       valid = True
#       self.prepare()


#     elif command == self.config.COMMAND_FLAG:
#       self.state = self.config.STATE_CONTINUE
#       answer = "FLAG"
#       valid = True
#       self.prepare()

#     else:
#       logger.info(f"undefined command {command} with content {args}")
#       self.state = self.config.STATE_CONTINUE
#       self.prepare()

#     new_response = {
#       'valid': valid,
#       'answer': answer,
#       'document': document,
#       'page': page,
#       'score': score
#     }

#     self.data.pop(0)
#     self.data.append(new_response)

#     shared.update_response((id, self.data))


class AnswerText(AbstractFlow):
  def __init__(self,
               config: "Config",
               agents: Dict[str, "Agent"],
               id: str,
    ) -> None:
    super().__init__(config)
    self.agents = agents
    self.current_agent = self.agents.get("init", None)
    self.id = id
    assert type(self.current_agent) != type(None), "Failed to load initial agent"

    self.input = {"question": "", "text": ""}
    self.mem = ""
    self.state: str = self.config.STATE_NONE
    self.set_agent_dict()
    self.data = None

  def pre_execute_loop(self, content: Dict[str, str]) -> None:
    """
    Update self params befor executing loop
    """
    self.input["question"] = content["question"]
    self.input["text"] = content["text"]
    self.current_agent = self.agents["init"]
    self.state: str = self.config.STATE_RUN
 
  def execute(self, data: Dict[str,Any]) -> None:
    """
    Execute command
    """
    conn = create_connection(db_file)

    command_name, args = self.parse_command(data)
    command = command_name.upper()

    if command == self.config.COMMAND_ANSWER:
      answer = data.get("answer", data)
      if type(answer) is not str:
        answer = str(answer)
      # answer = data.get("answer", str(data))
      valid = "True"

    elif command == self.config.COMMAND_FLAG:
      answer = f"FLAG:\n{data['answer']}"
      valid = "False"

    else:
      logger.info(f"undefined command {command} with content {args}")
      answer = f"UNKNOWN:\n{data['answer']}"
      valid = "False"

    self.state = self.config.STATE_CONTINUE
    update_answer(conn, self.id, valid, answer)
