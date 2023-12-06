from pipeline.shared_content import logger
from pipeline.config.config import config
from pipeline.functions.VectorDB import vectordb
from pipeline.agent.instantiations.agent_enhance import enhance_question
from pipeline.agent.instantiations.agent_answer_question import gen_agent
from pipeline.functions.ParseToJson import loadString
from pipeline.flows.answer_from_text import AnswerPdf
from pipeline.flows.answer_from_text import AnswerText
from app.functions.db import create_connection, create_answer, update_query, get_answer_text
import threading
from db import db_path

# db_file = '../db/mysql/database.db'
db_file = db_path  # f'{db_path}/mysql/database.db'


def run_query(question, id):
    conn = create_connection(db_file)

    # ENHANCE
    logger.log("run_query: ENHANCE")
    try:
        additional_questions_raw = enhance_question.talk(question)
        print(additional_questions_raw)
        additional_questions = loadString(additional_questions_raw, format={
            "questions": "[list of questions]"})
        questions = question + \
            " ".join(additional_questions.get("questions", []))

    except Exception as e:
        logger.warning(f"fail to run question: {question} with error: {e}")
        questions = question

    update_query(conn, id, search_query=questions)

    # VECTOR SEARCH
    logger.log("run_query: VECTOR SEARCH")
    answers = []
    results = vectordb.similarity_search_with_score(question, k=10)
    for res in results:
        answer_id = create_answer(
            conn=conn,
            query_id=id,
            score=res[1],
            document=res[0].metadata['document'],
            page=res[0].metadata['page'],
            text=res[0].page_content
        )
        answers.append(answer_id)

    update_query(conn, id, status='Summarizing')

    # CREATE THREADS FOR ANSWERS
    logger.log("run_query: CREATE THREADS FOR ANSWERS")
    for answer_id in answers:
        text = get_answer_text(conn, answer_id=answer_id)
        content = {"question": question, "text": text}
        answer_questions_flow = AnswerText(
            config, agents={"init": gen_agent()}, id=answer_id)
        agent = threading.Thread(
            target=answer_questions_flow.run, args=[content])
        agent.start()

    update_query(conn, id, status='Summarizing +')

    logger.log("run_query: DONE")
