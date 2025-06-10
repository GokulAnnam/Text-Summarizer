

from flask import Flask, request, jsonify, session, redirect, url_for
from database import init_db, SessionLocal
from models.User import User
from models.Summary import Summary
from dotenv import load_dotenv
import os
from flask_cors import CORS
from transformers import pipeline
from flask_session import Session
import secrets 
import bcrypt  

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.textSummarizer.pipeline.prediction import PredictionPipeline

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", 'dev_secret_key')
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  
app.config["SESSION_COOKIE_SECURE"] = False 
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_NAME"] = os.getenv('COOKIE', 'session')
app.config["PERMANENT_SESSION_LIFETIME"] = 86400  

Session(app)

init_db()

summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="google/pegasus-xsum")
    return summarizer


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ["email", "password", "name"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    
   
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    
    
    session_db = SessionLocal()
    existing_user = session_db.query(User).filter_by(email=email).first()
    
    if existing_user:
        session_db.close()
        return jsonify({"error": "Email already registered"}), 409
    
  
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  
    new_user = User(
        email=email,
        name=name,
        password_hash=hashed_password.decode('utf-8')  
    )
    
    session_db.add(new_user)
    session_db.commit()
    session_db.refresh(new_user)
    print(f"User logged in: ID={new_user.id}, Email={new_user.email}, Name={new_user.name}")

    session["user_id"] = new_user.id
    session["user_email"] = new_user.email
    session.modified = True
    
    session_db.close()
    
    return jsonify({
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing email or password"}), 400
    
    email = data.get("email")
    password = data.get("password")
    
    session_db = SessionLocal()
    user = session_db.query(User).filter_by(email=email).first()
    
    if not user or not user.password_hash:
        session_db.close()
        return jsonify({"error": "Invalid email or password"}), 401
    
 
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        session_db.close()
        return jsonify({"error": "Invalid email or password"}), 401
    

    session["user_id"] = user.id
    session["user_email"] = user.email
    session.modified = True
    print(f"User logged in: ID={user.id}, Email={user.email}, Name={user.name}")

 
    print(f"Session after login: user_id={session.get('user_id')}")
    
    session_db.close()
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    })


@app.route("/api/debug/session", methods=["GET"])
def debug_session():
    return jsonify({
        "has_session": bool(session),
        "user_id": session.get("user_id"),
        "session_keys": list(session.keys())
    })

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        print("No user_id in session:", dict(session))
        return None
    
    try:
        session_db = SessionLocal()
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()
        return user
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        return None

@app.route("/api/user", methods=["GET"])
def get_user():
   
    print(f"Session in /api/user: {dict(session)}")
    print(f"Request cookies: {request.cookies}")
    
    user = get_current_user()
    if not user:
        return jsonify({"isAuthenticated": False, "message": "No user in session"}), 401
    
    return jsonify({
        "isAuthenticated": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    })

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("user_email", None)
    session.modified = True
    return jsonify({"message": "Logged out successfully"})

@app.route("/api/summarize", methods=["POST"])
def summarize_api():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or 'input_text' not in data:
        return jsonify({"error": "Missing input text"}), 400
    
    input_text = data.get("input_text")
    summary_type = data.get("summary_type", "short")
    try:
        predictor = PredictionPipeline()
        summary = predictor.predict(input_text)

        session_db = SessionLocal()
        record = Summary(
            input_text=input_text,
            summary_text=summary,
            summary_type=summary_type,
            user_id=user.id
        )
        session_db.add(record)
        session_db.commit()
        session_db.close()

        return jsonify({
            "input_text": input_text, 
            "summary": summary,
            "summary_type": summary_type
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate summary: {str(e)}"}), 500

@app.route("/api/history", methods=["GET"])
def history_api():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    session_db = SessionLocal()
    summaries = session_db.query(Summary).filter_by(user_id=user.id).order_by(Summary.created_at.desc()).limit(10).all()
    session_db.close()

    summary_data = [{
        "id": s.id,
        "input_text": s.input_text, 
        "summary_text": s.summary_text,
        "summary_type": s.summary_type,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in summaries]
    
    return jsonify(summary_data)

if __name__ == "__main__":
    app.run(debug=True)
from fastapi import FastAPI
import uvicorn
import sys
import os
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from fastapi.responses import Response
from src.textSummarizer.pipeline.prediction import PredictionPipeline

text: str = "What is Text Summarization"

app = FastAPI()

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def training():
    try:
        os.system("python main.py")
        return Response("Training successful !!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")
    
@app.post("/predict")
async def predict_route(text: str, summary_type: str = "short"):
    try:
        obj = PredictionPipeline()
        # Pass the summary_type to the predict method
        summary = obj.predict(text, summary_type)
        return {"summary": summary}
    except Exception as e:
        raise e
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
