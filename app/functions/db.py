import sqlite3
from sqlite3 import Error, Connection
from typing import Dict, Any, Optional, List
from pipeline.shared_content import logger

db_file = '../../db/mysql/database.db'


def create_connection(db_file) -> Connection:
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        logger.error(f"SQL: create_connection: {e}")

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        logger.error(f"SQL: create_table: {e}")


def gen_tables(conn):
    """
        Create queries table: id, question, status, search_query
        Create answers table: id, query_id, score, valid, document, page, text, answer
    """
    sql_create_queries_table = """ CREATE TABLE IF NOT EXISTS queries (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        question text NOT NULL,
                                        status text NOT NULL,
                                        search_query text,
                                        date text
                                    ); """

    sql_create_answers_table = """CREATE TABLE IF NOT EXISTS answers (
                                    id integer PRIMARY KEY AUTOINCREMENT ,
                                    query_id integer NOT NULL,
                                    valid text,
                                    score real,
                                    document text NOT NULL,
                                    page integer NOT NULL,
                                    text text NOT NULL,
                                    answer text,
                                    FOREIGN KEY (query_id) REFERENCES queries (id)
                                );"""

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_queries_table)

        # create tasks table
        create_table(conn, sql_create_answers_table)
    else:
        logger.error(f"SQL: Error! cannot create the database connection.")

def create_query(conn: Connection, question: str) -> int:
    """
    Create a new project into the projects table
    :param conn:
    :param question:
    :return: query id
    """
    sql = ''' INSERT INTO queries(question,status)
              VALUES(?,?) '''
    initial_status = 'Initiated'
    cur = conn.cursor()
    cur.execute(sql, (question, initial_status))
    conn.commit()

    if cur.lastrowid is None:
        logger.error(f"SQL: Fail to create new query for question: {question}")
        raise Exception(f"Fail to create new query for question: {question}")
    return cur.lastrowid


def create_answer(conn: Connection,
                  query_id: int,
                  score: float,
                  document: str,
                  page: int,
                  text: str,
                  answer: Optional[str] = None
                  ) -> int:
    """
    Create a new answer into the answers table
    :param conn:
    :param query_id:
    :param score:
    :param document:
    :param page:
    :param text:
    :param answer:
    :return: query id
    """
    sql = ''' INSERT INTO answers(query_id,valid,score,document,page,text,answer)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    valid = True if answer else None
    cur.execute(sql, (query_id, valid, score, document, page, text, answer))
    conn.commit()

    if cur.lastrowid is None:
        logger.error(f"SQL: Fail to create new answer for query_id: {query_id}")
        raise Exception(f"Fail to create new answer for query_id: {query_id}")
    return cur.lastrowid


def update_query(conn: Connection,
                 query_id: str,
                 status: Optional[str] = None,
                 search_query: Optional[str] = None
                 ) -> bool:
    is_success = True
    if search_query:
        is_success = update_query_search_query(conn, 
            query_id, search_query) and is_success

    if status:
        is_success = update_query_status(conn, query_id, status) and is_success

    return is_success


def update_query_status(conn: Connection, query_id: int, status: str) -> bool:
    """
    update status of a query
    :param conn:
    :param query_id:
    :param status:
    :return: project id
    """
    sql = ''' UPDATE queries
              SET status = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    try:
        cur.execute(sql, [status, query_id])
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"SQL: update_query_status: {e}")
        return False

def update_query_search_query(conn: Connection, query_id: int, search_query: str) -> bool:
    """
    update status of a query
    :param conn:
    :param query_id:
    :param search_query:
    :return: project id
    """
    sql = ''' UPDATE queries
              SET search_query = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    try:
        cur.execute(sql, [search_query, query_id])
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"SQL: update_query_search_query: search_query: {search_query}\n query_id: {query_id} \n error: {e}")
        return False


def update_answer(conn: Connection, answer_id: int, valid: Optional[bool], answer: Optional[str]) -> bool:
    """ update answer with answer and validity """
    is_success = True
    if answer:
        is_success = update_answer_answer(conn, 
            answer_id, answer) and is_success

    if valid:
        is_success = update_answer_valid(conn, answer_id, valid) and is_success

    return is_success


def update_answer_answer(conn: Connection, answer_id: int, answer: str) -> bool:
    """
    update status of a answer
    :param conn:
    :param answer_id:
    :param answer:
    :return: project id
    """
    sql = ''' UPDATE answers
              SET answer = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    try:
        cur.execute(sql, [answer, answer_id])
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"SQL: update_answer_answer: query: {sql} \n answer: {answer} \n answer_id: {answer_id} \n error: {e}")
        return False

def update_answer_valid(conn: Connection, answer_id: int, valid: bool) -> bool:
    """
    update status of a answer
    :param conn:
    :param answer_id:
    :param valid:
    :return: project id
    """
    sql = ''' UPDATE answers
              SET valid = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    try:
        cur.execute(sql, [valid, answer_id])
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"SQL: update_answer_valid: query: {sql} \n valid: {valid} \n answer_id: {answer_id}\n error:{e}")
        return False


def get_answer(conn: Connection, answer_id: int) -> Dict[str, Any]:
    """
    select * of a answers
    :param conn:
    :param answer_id:
    :return: {
        id,
        query_id,
        valid,
        score,
        document,
        page,
        text,
        answer
    }
    """
    sql = ''' SELECT * 
            FROM answers
                WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, [answer_id])
    id, query_id, valid, score, document, page, text, answer = cur.fetchone()

    return {
        'id': id,
        'query_id': query_id,
        'valid': valid,
        'score': score,
        'document': document,
        'page': page,
        'text': text,
        'answer': answer
    }


def get_answer_text(conn: Connection, answer_id: int) -> str:
    return get_answer(conn, answer_id)['text']


def get_answers_for_query(conn: Connection, query_id: int) -> List[Dict[str, Any]]:
    sql = ''' SELECT id 
        FROM answers
            WHERE query_id = ?'''
    cur = conn.cursor()
    answers_id = cur.execute(sql, [query_id])
    all_answers = [get_answer(conn, answer_id[0]) for answer_id in answers_id]
    return all_answers


def get_query(conn: Connection, query_id: int) -> Dict[str, Any]:
    answers = get_answers_for_query(conn, query_id)
    question = get_query_question(conn, query_id)
    status = get_query_status(conn, query_id)
    search_query = get_query_search_query(conn, query_id)
    return {'question': question, 'answers': answers, 'status': status, 'search_query': search_query}


def get_query_question(conn: Connection, query_id: int) -> str:
    """
    select question of a query
    :param conn:
    :param query_id:
    :return: question[text]
    """
    sql = ''' SELECT question 
            FROM queries
                WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, [query_id])
    return cur.fetchone()[0]


def get_query_status(conn: Connection, query_id: int) -> str:
    """
    select question of a query
    :param conn:
    :param query_id:
    :return: status[text]
    """
    sql = ''' SELECT status 
            FROM queries
                WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, [query_id])
    return cur.fetchone()[0]


def get_query_search_query(conn: Connection, query_id: int) -> Optional[str]:
    """
    select question of a query
    :param conn:
    :param query_id:
    :return: search_query[text]
    """
    sql = ''' SELECT search_query 
            FROM queries
                WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, [query_id])
    return cur.fetchone()[0]
