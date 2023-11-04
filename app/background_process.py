from pipeline.shared_content import logger, shared, status
from pipeline.config.config import config
from pipeline.functions.VectorDB import vectordb
from pipeline.agent.instantiations.agent_enhance import enhance_question
from pipeline.agent.instantiations.agent_answer_question import answer_agent
from pipeline.functions.ParseToJson import loadString
from pipeline.flows.answer_from_text import AnswerPdf

import time


def be_run():
    while True:
        query_obj = shared.get_query()
        if not query_obj:
            time.sleep(10)
            continue

        id = query_obj["id"]
        logger.info(f"resolving query id: {id}")
        status.set_state(config.STATE_RUN)

        question = query_obj.get("question", "")


        # if enhance:
        additional_questions_raw = enhance_question.talk(question)
        additional_questions = loadString(additional_questions_raw)
        questions = question + " ".join(additional_questions.get("questions", []))

        answer = []
        results = vectordb.similarity_search_with_score(questions, k=10)
        for res in results:
            answer.append({'document': res[0].metadata['document'],
                       'page': res[0].metadata['page'], 'score': res[1], 'answer': None, 'valid': None})

        shared.update_response((id, answer))

        # if summary:   
        answer_questions_flow = AnswerPdf(config, agents={"init": answer_agent}, id=id)
        answer_questions_flow.run(question)

        logger.info(f"done resolving query id {id}")
        status.set_state(config.STATE_READY)
