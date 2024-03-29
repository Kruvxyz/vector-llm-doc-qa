import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from pipeline.functions.ParseToJson import loadString
from pipeline.shared_content import current_chat, logger, status
import os.path as path

class AbstractFlow:
  def __init__(self, config: "Config") -> None:
    """
    Define agents here
    """
    self.config = config
    self.file_name: str = "output.txt"
    self.agents: Dict[str, "Agent"] = {}
    self.current_agent: Optional["Agent"] = None
    self.input: Any = ""  # input to propagate between states
    self.mem: str = "" # memory
    self.state: str = self.config.STATE_NONE
    self.agent_dict = {}

  def set_agent_dict(self) -> None:
    self.agent_dict = {self.agents[name]: name for name in self.agents}
    logger.info(f"flow: set_agent_dict: {str(self.agent_dict)}")

  def get_current_agent_state(self) -> str:
    current_agent_state = self.agent_dict.get(self.current_agent, None)  
    assert type(current_agent_state) != type(None), "Current agent state is not defined"
    return current_agent_state

  # def get_max_num_of_tokens(self) -> int:
  #   """
  #   Return maximum possible token per chunk
  #   Should consider internal / external intercace
  #   Calculation is somthing like:
  #   return max_tokens - max([agent.get_expected_converation_tokens() for agent in self.agents])
  #   """
  #   return 0
  
  def run(self, content: Any = "", prints: bool = True) -> Optional[str]:
    """Execute FSM

    Args:
      content (Any): string or dict contains flow initial data
      prints (bool): print agent process

    Returns:
      TBD
    """
    logger.info("flow: run")
    self.pre_execute_loop(content)
    logger.info("flow: run pre_execute_loop complete")

    while True:
      force_state = status.get_state()
      if force_state is not None:
        self.state = force_state
        status.clean_state()
      logger.info(f"flow: state: {self.state}")

      if self.state == self.config.STATE_RUN:
        if type(self.input) is str:
          prompt = self.current_agent.prepare_agent_prompt(self.input)
        elif type(self.input) is dict: 
          prompt = self.current_agent.prepare_agent_prompt("", self.input)
        else:
          raise TypeError("flow->input type must be str or dict")

        raw_answer = self.current_agent.talk(prompt)

        logger.info(f"flow: raw_answer: {raw_answer}")
        answer = loadString(raw_answer, self.current_agent.response_format)
        logger.info(f"------------------{self.agent_dict[self.current_agent]}--------------------")
        logger.info(answer)
        if prints:
          command_name, args = self.parse_command(answer)
          command = command_name.upper()
          logger.info(f"thoughts: {answer.get('thoughts')}")
          logger.info(f"command: {command}")
          logger.info(f"args: {str(args)}")
        logger.info("--------------------------------------")
        current_chat.append({
          "agent": self.agent_dict[self.current_agent],
          "system": self.current_agent.system_prompt,
          "prompt": prompt,
          "response": answer})
        self.execute(answer)

      elif self.state == self.config.STATE_PAUSE:
        logger.info("flow: state: STATE_PAUSE")
        time.sleep(60)

      else:
        break

    return None

  def pre_execute_loop(self, content: Any) -> None:
    """Update self params befor executing loop

    Args:
      content (Any): flow initial data

    Returns:
        None
    """
    self.state = self.config.STATE_RUN
    self.input = content

  def parse_command(self, data: Dict[str,Any]) -> Tuple[str, Dict[str, str]]:
    """Parse AI answer in Json format and return command and args

    Args:
      data (json): AI answer formatted as Json
      sensitive: raise alert if no command in data

    Returns:
        Command (str): Next action
        Args Dict[str, str]: argument with key values and values

    """
    command_dict = data.get("command", "")
    assert "name" in command_dict
    command_name = command_dict["name"]
    # verify command is one word:
    command_name_list = command_name.split()
    if  len(command_name_list) > 1:
      command_name = command_name_list[0]
    return command_name, command_dict.get("args", {})

  def execute(self, data: Dict[str,Any]) -> None:
    """Execute command
    fixme(guyhod): should be a generetad function. This function should be generated at cunstruction phase based on list of commands (should pass when __init__ is callled).

    Args:
      data (json): AI answer formatted as Json

    Returns:
      None
    """
    command_name, args = self.parse_command(data)
    command = command_name.upper()

    if command == self.config.COMMAND_END_FLOW:
      self.state = self.config.STATE_CONTINUE

  # def append_to_file(self, text: str) -> None:
  #   file_path = path.join("outputs/", self.config.output_file_name)
  #   f = open(file_path, "a")
  #   f.write(text + "\n")
  #   f.close()