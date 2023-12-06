from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import threading 
from pipeline.shared_content import status, logger
from app.functions import api_code_validation
from app.functions.db import create_connection, get_query, create_query, gen_tables
from pipeline.config.config import config
from app.load_documents import load_docs
from dotenv import load_dotenv
import os
from openai import OpenAI
from db import db_path
load_dotenv()
config.ai["provider"] = os.getenv("LLM_PROVIDER")
config.open_ai_key = os.getenv("API_KEY", "")
config.model = os.getenv("OPENAI_MODEL", "gpt-4")
config.ai["model"] = config.model

if config.ai["provider"] == 'openai':
    client = OpenAI(api_key=config.open_ai_key)
    config.ai["ai"] = client

# db_file = f'{db_path}/mysql/database.db'
db_file = db_path

from app.background_process import be_run, run_query


app = Flask(__name__)
cors = CORS(app)


# pipeline = threading.Thread(target=load_docs)
# pipeline.start()

@app.route('/ping', methods=['POST', 'GET'])
@cross_origin()
def ping():
    logger.info("APP: ping")
    return 'pong'


@app.route('/state', methods=['POST'])
@cross_origin()
@api_code_validation
def state():
    logger.info(f"APP: state: {str(status.get_state())}")
    return jsonify({"status": "ok", "state": str(status.get_state())})


@app.route('/restart', methods=['POST'])
@cross_origin()
@api_code_validation
def restart():
    logger.info("APP: restart")
    conn = create_connection(db_file)
    gen_tables(conn)
    return jsonify({"status": "ok"})


@app.route('/load', methods=['POST'])
@cross_origin()
@api_code_validation
def load():
    logger.info("APP: load")
    pipeline = threading.Thread(target=load_docs)
    pipeline.start()
    return jsonify({"status": str(status.get_state())})


@app.route('/query', methods=['POST'])
@cross_origin()
@api_code_validation
def query():
    logger.info("APP: query")
    if status.get_state() == config.STATE_LOADING:
        logger.warning("APP: query: STATE_LOADING")
        return jsonify({"status": "fail"})

    data = request.get_json()
    question = data.get("question")
    conn = create_connection(db_file)
    id = create_query(conn, question)
    be = threading.Thread(target=run_query, args=[question, id])
    be.start()

    logger.info(f"APP: query: id: {id}")
    return jsonify({"status": "ok", "id": id})


@app.route('/read', methods=['POST'])
@cross_origin()
@api_code_validation
def read():
    logger.info("APP: read")
    data = request.get_json()
    id = data.get("id")
    conn = create_connection(db_file)
    response = get_query(conn, id)
    answers = []
    for answer in response.get("answers", []):
        if answer['valid'] is not None:
            answer['valid'] = True if answer['valid']=="True" else False 
        answers.append(answer)
    response['answer'] = answers
    return jsonify(response)
