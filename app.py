from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import re
import logging
from pathlib import Path
from utils.yaml_collection import YamlCollection
from utils.database.connection import DatabaseConnection
from utils.metrics_analyzer import MetricsAnalyzer

app = Flask(__name__)
CORS(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

yaml_collection = YamlCollection()
metrics_analyzer = MetricsAnalyzer()

@app.before_request
def filter_bad_requests():
    if request.method == 'GET' and request.path == '/':
        return jsonify({"message": "API is running", "endpoints": ["/api/chat", "/api/metrics"]}), 200
    
    if request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']:
        return jsonify({"error": "Method not allowed"}), 405
    
    try:
        if request.content_length and request.content_length > 0:
            if not request.is_json and request.content_type and 'application/json' in request.content_type:
                return jsonify({"error": "Invalid content type"}), 400
    except:
        pass

@app.errorhandler(400)
def handle_bad_request(e):
    if hasattr(e, 'description') and 'Bad request version' in str(e.description):
        return '', 400
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(Exception)
def handle_exception(e):
    if 'Bad request version' in str(e):
        return '', 400
    return jsonify({"error": str(e)}), 500

def load_system_prompt():
    base_dir = Path(__file__).parent
    prompt_file = base_dir / "config" / yaml_collection.get_lm_system_prompt()
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()

def clean_markdown(text):
    import re
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'_{2,}', '', text)
    text = re.sub(r'~{2,}', '', text)
    return text.strip()

def call_gemini_api(user_prompt):
    api_key = yaml_collection.get_lm_api_key()
    base_url = yaml_collection.get_lm_base_url()
    model = yaml_collection.get_lm_model()
    
    if ":" in model:
        model_name = model.split(":")[0]
    else:
        model_name = model
    
    url = f"{base_url}/{model_name}:generateContent"
    
    system_prompt = load_system_prompt()
    
    payload = {
        "contents": [{
            "parts": [{
                "text": user_prompt
            }]
        }],
        "systemInstruction": {
            "parts": [{
                "text": system_prompt
            }]
        }
    }
    
    params = {
        "key": api_key
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, params=params, headers=headers)
        
        if response.status_code == 403:
            error_detail = response.text
            if "API key not valid" in error_detail or "permission" in error_detail.lower():
                return f"Lỗi: API key không hợp lệ hoặc không có quyền truy cập model '{model_name}'. Vui lòng kiểm tra lại API key trong Google Cloud Console."
            elif "location" in error_detail.lower() or "region" in error_detail.lower():
                return f"Lỗi: Vị trí địa lý không được hỗ trợ hoặc model '{model_name}' không khả dụng. Thử đổi model khác như 'gemini-1.5-pro' hoặc 'gemini-1.5-flash'."
            else:
                return f"Lỗi 403: {error_detail[:200]}"
        
        response.raise_for_status()
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned_response = clean_markdown(ai_response)
            return cleaned_response
        else:
            return "Không thể nhận được phản hồi từ AI."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return f"Lỗi 403: API key không có quyền hoặc model '{model_name}' không khả dụng. Vui lòng kiểm tra lại."
        return f"Lỗi HTTP {e.response.status_code}: {str(e)}"
    except Exception as e:
        return f"Lỗi khi gọi API: {str(e)}"

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_prompt = data.get("prompt", "")
        
        if not user_prompt:
            return jsonify({"error": "Prompt không được để trống"}), 400
        
        ai_response = call_gemini_api(user_prompt)
        
        metrics = metrics_analyzer.analyze(user_prompt, ai_response)
        
        db_conn = DatabaseConnection()
        if db_conn.connect():
            try:
                insert_query = """
                INSERT INTO uit.dbo.TUDUYAI_USER_PROMPT 
                (USER_PROMPT, IS_DISADVANTAGE, AI_RESPONSE, IS_HAVING_VERIFICATION, 
                 IS_HAVING_DISCLAIMER, PROMPT_INJECTION_NUMBER, PROMPT_INJECTION_ATTEMPT_NUMBER,
                 EXACT_CALCULATION_NUMBER, CALCULATION_NUMBER, IS_HAVING_SYMPATHY,
                 IS_SUCCESSFULLY_VALIDATE_INPUT, IS_HAVING_BIAS, IS_APPROPRIATE_CONTEXT,
                 IS_EASY_TO_UNDERSTAND_FOR_DISADVANTAGE, IS_HAVING_EXPLANATION)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    user_prompt,
                    metrics["is_disadvantage"],
                    ai_response,
                    metrics["is_having_verification"],
                    metrics["is_having_disclaimer"],
                    metrics["prompt_injection_number"],
                    metrics["prompt_injection_attempt_number"],
                    metrics["exact_calculation_number"],
                    metrics["calculation_number"],
                    metrics["is_having_sympathy"],
                    metrics["is_successfully_validate_input"],
                    metrics["is_having_bias"],
                    metrics["is_appropriate_context"],
                    metrics["is_easy_to_understand_for_disadvantage"],
                    metrics["is_having_explanation"]
                )
                
                db_conn.execute_non_query(insert_query, params)
            finally:
                db_conn.close()
        
        return jsonify({
            "response": ai_response,
            "metrics": metrics
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    try:
        db_conn = DatabaseConnection()
        if db_conn.connect():
            try:
                query = """
                SELECT 
                    COUNT(*) as total_prompts,
                    SUM(CASE WHEN IS_DISADVANTAGE = 'Y' THEN 1 ELSE 0 END) as disadvantage_count,
                    SUM(CASE WHEN IS_HAVING_VERIFICATION = 'Y' THEN 1 ELSE 0 END) as verification_count,
                    SUM(CASE WHEN IS_HAVING_DISCLAIMER = 'Y' THEN 1 ELSE 0 END) as disclaimer_count,
                    SUM(CASE WHEN IS_HAVING_SYMPATHY = 'Y' THEN 1 ELSE 0 END) as sympathy_count,
                    SUM(CASE WHEN IS_HAVING_BIAS = 'Y' THEN 1 ELSE 0 END) as bias_count,
                    SUM(CASE WHEN IS_APPROPRIATE_CONTEXT = 'Y' THEN 1 ELSE 0 END) as appropriate_context_count,
                    SUM(CASE WHEN IS_EASY_TO_UNDERSTAND_FOR_DISADVANTAGE = 'Y' THEN 1 ELSE 0 END) as easy_understand_count,
                    SUM(CASE WHEN IS_HAVING_EXPLANATION = 'Y' THEN 1 ELSE 0 END) as explanation_count,
                    SUM(EXACT_CALCULATION_NUMBER) as total_exact_calc,
                    SUM(CALCULATION_NUMBER) as total_calc,
                    SUM(PROMPT_INJECTION_NUMBER) as total_injection_detected,
                    SUM(PROMPT_INJECTION_ATTEMPT_NUMBER) as total_injection_attempt,
                    SUM(CASE WHEN IS_SUCCESSFULLY_VALIDATE_INPUT = 'Y' THEN 1 ELSE 0 END) as validation_count
                FROM uit.dbo.TUDUYAI_USER_PROMPT
                """
                
                result = db_conn.execute_query(query)
                if result and len(result) > 0:
                    row = result[0]
                    total = row[0] or 0
                    
                    if total > 0:
                        metrics_data = {
                            "total_prompts": total,
                            "ecr": (row[8] or 0) / total * 100,
                            "vs": (row[2] or 0) / total * 100,
                            "bdr": (row[5] or 0) / total * 100,
                            "las": (row[7] or 0) / (row[1] or 1) * 100 if (row[1] or 0) > 0 else 0,
                            "cas": (row[6] or 0) / total * 100,
                            "uir": (row[3] or 0) / total * 100,
                            "nps": (row[9] or 0) / (row[10] or 1) * 100 if (row[10] or 0) > 0 else 0,
                            "pidr": (row[11] or 0) / (row[12] or 1) * 100 if (row[12] or 0) > 0 else 0,
                            "ivsr": (row[13] or 0) / total * 100,
                            "eir": (row[4] or 0) / (row[1] or 1) * 100 if (row[1] or 0) > 0 else 0
                        }
                    else:
                        metrics_data = {
                            "total_prompts": 0,
                            "ecr": 0, "vs": 0, "bdr": 0, "las": 0, "cas": 0,
                            "uir": 0, "nps": 0, "pidr": 0, "ivsr": 0, "eir": 0
                        }
                    
                    return jsonify(metrics_data)
                else:
                    return jsonify({
                        "total_prompts": 0,
                        "ecr": 0, "vs": 0, "bdr": 0, "las": 0, "cas": 0,
                        "uir": 0, "nps": 0, "pidr": 0, "ivsr": 0, "eir": 0
                    })
            finally:
                db_conn.close()
        
        return jsonify({
            "total_prompts": 0,
            "ecr": 0, "vs": 0, "bdr": 0, "las": 0, "cas": 0,
            "uir": 0, "nps": 0, "pidr": 0, "ivsr": 0, "eir": 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import sys
    import logging
    
    logging.basicConfig(level=logging.ERROR)
    
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.CRITICAL)
    
    class FilterBadRequests(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'getMessage'):
                return True
            try:
                message = str(record.getMessage())
                if any([
                    'Bad request version' in message,
                    'Bad HTTP/0.9 request type' in message,
                    'Bad HTTP' in message and 'request' in message,
                    'code 400' in message and ('\\x16' in message or '\x16' in message)
                ]):
                    return False
            except:
                pass
            return True
    
    for handler in werkzeug_logger.handlers:
        handler.addFilter(FilterBadRequests())
    
    werkzeug_logger.addFilter(FilterBadRequests())
    
    app.logger.setLevel(logging.ERROR)
    
    app.run(host="0.0.0.0", port=5000, debug=True)

