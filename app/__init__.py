from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pipeline.shared_content import agents, current_chat, history, status, logger, shared
import threading
from app.functions import api_code_validation
from pipeline.config.config import config
from app.load_documents import load_docs
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
config.ai["provider"] = os.getenv("LLM_PROVIDER")
config.open_ai_key = os.getenv("API_KEY", "")
config.model = os.getenv("OPENAI_MODEL", "gpt-4")
config.ai["model"] = config.model

if config.ai["provider"] == 'openai':
    client = OpenAI(api_key=config.open_ai_key)
    config.ai["ai"] = client


app = Flask(__name__)
cors = CORS(app)


pipeline = threading.Thread(target=load_docs)
pipeline.start()

from app.background_process import be_run, run_query
be = threading.Thread(target=be_run)
be.start()


@app.route('/ping', methods=['POST', 'GET'])
@cross_origin()
def ping():
    return 'pong'


@app.route('/state', methods=['POST'])
@cross_origin()
@api_code_validation
def state():
    return jsonify({"status": "ok", "state": str(status.get_state())})


@app.route('/restart', methods=['POST'])
@cross_origin()
@api_code_validation
def restart():
    shared.restart()
    return jsonify({"status": "ok"})


@app.route('/query', methods=['POST'])
@cross_origin()
@api_code_validation
def query():


    if status.get_state() == config.STATE_LOADING:
        return jsonify({"status": "fail"})

    data = request.get_json()
    question = data.get("question")
    id = shared.add_query(question=question)
    be = threading.Thread(target=run_query, args=[question, id])
    be.start()
    
    return jsonify({"status": "ok", "id": id})


@app.route('/read', methods=['POST'])
@cross_origin()
@api_code_validation
def read():
    data = request.get_json()
    id = data.get("id")
    response = shared.get_response(id)
    return jsonify(response)
