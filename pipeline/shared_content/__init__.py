from typing import Dict, List, Tuple, Optional
from singleton_decorator import singleton
from dotenv import load_dotenv
import logging
import os
import string
import random

load_dotenv()

logging_file = os.getenv("LOGGING_FILE", "logs.log")
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                    filename=f"logs/{logging_file}", level=logging.DEBUG)
logger = logging.getLogger(__name__)


@singleton
class Shared:
    def __init__(self, num_digits: int = 12) -> None:
        # self.queue: List[Tuple[str, str]] = []
        self.query_queue: List[Dict[str, str]] = []
        self.responses: Dict[str, Optional[str]] = {}
        self.num_digits = num_digits

    def get_id(self, schedule_sec: int = 60*60*24) -> str:
        while True:
            new_id = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=self.num_digits))
            if new_id not in self.responses:
                self.update_response((new_id, None))
                return new_id

    # def get_question(self) -> Optional[Tuple[str, str]]:
    #     if len(self.queue) == 0:
    #         return None
    #     next_question = self.queue.pop(0)
    #     return next_question

    def get_query(self) -> Optional[Dict[str, str]]:
        if len(self.query_queue) == 0:
            return None
        next_query = self.query_queue.pop(0)
        if not type(next_query) is dict:
            raise TypeError("Must query with dict Dict[str, str]")
        return next_query

    def _add_query(self, new_query: Dict[str, str]) -> bool:
        self.query_queue.append(new_query)
        return True

    def add_query(self, question: str) -> Optional[str]:
        id = self.get_id()
        query = {'id': id, 'question': question}
        if self._add_query(query):
            return id
        else:
            return None

    def update_response(self, object: Tuple[str, Optional[List[str]]]) -> bool:
        id, response = object
        self.responses[id] = response
        return True

    def get_response(self, id: str) -> Dict[str, str]:
        try:
            response = self.responses[id]
        except KeyError:
            return {"status": "Unknown"}

        response_json = {"status": "WIP"}
        if response:
            response_json["status"] = "ok"
            response_json["answer"] = response

        return response_json


@singleton
class Status:
    def __init__(self):
        self.agent = ""
        self.status = ""
        self.state = None

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def clean_state(self):
        self.state = None


shared = Shared()

status = Status()
agents = {}
history = []
current_chat = []
