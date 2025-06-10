from flask import Flask, request, jsonify, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
from database import init_db, SessionLocal
from models.User import User
from models.Summary import Summary
from dotenv import load_dotenv
import os
from flask_cors import CORS
from transformers import pipeline


load_dotenv()

app = Flask(_name_)
app.secret_key = os.getenv('SECRET_KEY')
app.config["SESSION_COOKIE_NAME"] = os.getenv('COOKIE')


CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # or "Strict"
app.config["SESSION_COOKIE_SECURE"] = False

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("KEY"),
    client_secret=os.getenv("C_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={"access_type": "offline"},
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)


init_db()

summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    return summarizer

# OAuth callback route
@app.route("/login/callback")
def oauth_callback():
    try:
        token = google.authorize_access_token()  # <-- Get token from Google
        user_info = google.get('userinfo')       # <-- Get user info using the token
        user_data = user_info.json()             # <-- Parse JSON

        session["google_token"] = token
        session_db = SessionLocal()
        user = session_db.query(User).filter_by(oauth_user_id=user_data["id"]).first()
        if not user:
            user = User(
                oauth_user_id=user_data["id"],
                email=user_data["email"],
                name=user_data.get("name")
            )
            session_db.add(user)
            session_db.commit()

        session["user_id"] = user.id
        session_db.close()

        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}?login_success=true")
    
    except Exception as e:
        return jsonify({"error": f"OAuth callback failed: {str(e)}"}), 500


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    session_db = SessionLocal()
    user = session_db.query(User).filter_by(id=user_id).first()
    session_db.close()
    return user

@app.route("/api/user", methods=["GET"])
def get_user():
    user = get_current_user()
    if not user:
        return jsonify({"isAuthenticated": False}), 401
    
    return jsonify({
        "isAuthenticated": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    })

@app.route("/login")
def login():
    callback_url = url_for("oauth_callback", _external=True)
    return google.authorize(callback=callback_url)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("google_token", None)
    return jsonify({"message": "Logged out successfully"})


@app.route("/summarize", methods=["POST"])
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
        summarizer = get_summarizer()
        max_length = 60 if summary_type == "short" else 120
        summary = summarizer(input_text, max_length=max_length, min_length=20, do_sample=False)[0]["summary_text"]


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


@app.route("/history/api", methods=["GET"])
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