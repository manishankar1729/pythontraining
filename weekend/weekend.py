from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notepad.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False, default="")

# Create database tables
with app.app_context():
    db.create_all()

@app.route("/update", methods=['GET', 'POST'])
def index():
    note = Note.query.first()
    if not note:
        note = Note(content="")
        db.session.add(note)
        db.session.commit()

    if request.method == 'POST':
        new_content = request.form.get('content')
        if new_content:
            note.content = new_content
            db.session.commit()
    
    return render_template("index.html", content=note.content)

@app.route("/share", methods=['GET'])
def share():
    note = Note.query.first()
    return jsonify({"content": note.content if note else ""})

@app.route("/clearnotepadtxt", methods=['GET'])
def clear_notepad_txt():
    note = Note.query.first()
    if note:
        note.content = ""
        db.session.commit()
    return jsonify({"message": "Notepad content cleared"})

if __name__ == "__main__":
    app.run(debug=True)
