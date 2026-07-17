from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Load AI Model
model = joblib.load("models/student_model.pkl")


# ---- DATABASE INITIALIZATION ----
def init_db():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    # Safe structure checking: table automatically create ho jayegi agar missing hogi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            email TEXT,
            attendance REAL,
            study_hours REAL,
            assignment_marks REAL,
            quiz_marks REAL,
            previous_marks REAL,
            participation REAL,
            predicted_marks REAL,
            grade TEXT,
            risk TEXT
        )
    """)
    conn.commit()
    conn.close()

# Server start hone se pehle database setup check karna
init_db()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PREDICT ----------------

@app.route("/predict", methods=["POST"])
def predict():
    # Student Details
    name = request.form["name"]
    roll = request.form["roll"]
    email = request.form["email"]

    # Performance Details
    attendance = float(request.form["attendance"])
    study = float(request.form["study"])
    assignment = float(request.form["assignment"])
    quiz = float(request.form["quiz"])
    previous = float(request.form["previous"])
    participation = float(request.form["participation"])

    student = [[
        attendance,
        study,
        assignment,
        quiz,
        previous,
        participation
    ]]
    prediction = round(model.predict(student)[0], 2)

    # Risk mapping matches template thresholds exactly
    if prediction >= 85:
        grade = "A"
        risk = "Low Risk"
    elif prediction >= 70:
        grade = "B"
        risk = "Medium Risk"
    else:
        grade = "C"
        risk = "High Risk"

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students(
            name, roll, email, attendance, study_hours, 
            assignment_marks, quiz_marks, previous_marks, 
            participation, predicted_marks, grade, risk
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        name, roll, email, attendance, study, 
        assignment, quiz, previous, participation, 
        prediction, grade, risk
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        marks=prediction,
        grade=grade,
        risk=risk
    )


# ---------------- HISTORY ----------------

@app.route("/history")
def history():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    
    # Sorting from newest to oldest for better dashboard flow
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    students = cur.fetchall()
    
    conn.close()

    return render_template(
        "history.html",
        students=students
    )


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE risk='Low Risk'")
    low = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE risk='Medium Risk'")
    medium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE risk='High Risk'")
    high = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        low=low,
        medium=medium,
        high=high
    )


# ---------------- DELETE STUDENT ----------------

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/history")


# ---------------- EXPORT CSV ----------------

@app.route("/export")
def export():
    conn = sqlite3.connect("students.db")

    df = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )
    conn.close()

    df.to_csv(
        "students_report.csv",
        index=False
    )

    return send_file(
        "students_report.csv",
        as_attachment=True
    )


# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)