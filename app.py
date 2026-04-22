import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Science Tracker", layout="wide")

DATA_FILE = "data.json"

TOPICS = [
    "Scientific Skills",
    "Cell",
    "Coordination and Response",
    "Reproduction",
    "Matter",
    "Periodic Table",
    "Air",
    "Heat"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

def average(scores):
    return sum(scores) / len(scores) if scores else 0

def student_average(student):
    all_scores = []
    for topic in student:
        all_scores.extend(student[topic])
    return average(all_scores)

def weakest_topic(student):
    avg = {}
    for topic, scores in student.items():
        if scores:
            avg[topic] = average(scores)
    return min(avg, key=avg.get) if avg else None

st.title("Form 1 Science Tracker")

# =========================
# SIDEBAR - CONTROL PANEL
# =========================

# ---------- STUDENT MANAGEMENT ----------
st.sidebar.header("Student Management")

with st.sidebar.expander("Add Student"):
    name = st.text_input("Student Name")

    if st.button("Add Student"):
        if name and name not in data:
            data[name] = {t: [] for t in TOPICS}
            save_data(data)
            st.success(f"{name} added")
        elif name in data:
            st.error("Student already exists")

with st.sidebar.expander("Delete Student"):
    if data:
        student_to_delete = st.selectbox("Select Student", list(data.keys()))
        confirm = st.checkbox("Confirm delete")

        if st.button("Delete Student"):
            if confirm:
                del data[student_to_delete]
                save_data(data)
                st.success("Student deleted")
            else:
                st.error("Please confirm first")
    else:
        st.info("No students available")

# ---------- SCORE MANAGEMENT ----------

if data:
    student = st.selectbox("Student", list(data.keys()), key="score_student")
    topic = st.selectbox("Topic", TOPICS)
    score = st.number_input("Score", 0, 100)

    if st.button("Add Score"):
        data[student][topic].append(score)
        save_data(data)
        st.success("Score added")


# ---------- DISPLAY ----------
if data:
    rows = []
    for s, t in data.items():
        avg = student_average(t)
        weak = weakest_topic(t)

        rows.append({
            "Student": s,
            "Average": round(avg, 2),
            "Weakest Topic": weak
        })

    df = pd.DataFrame(rows)

    # ---------- TWO COLUMN DASHBOARD ----------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Class Overview")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("Students to Focus")

        weak_students = df[df["Average"] < 50]

        if not weak_students.empty:
            st.write(weak_students)
        else:
            st.write("No weak students")

    # ---------- STUDENT PROGRESS GRAPH ----------
    st.subheader("Student Progress")

    selected_student = st.selectbox("Select Student for Graph", list(data.keys()))
    student_data = data[selected_student]

    topic_scores = []
    topic_names = []

    for topic, scores in student_data.items():
        if scores:
            topic_names.append(topic)
            topic_scores.append(sum(scores) / len(scores))

    if topic_scores:
        chart_data = pd.DataFrame({
            "Topic": topic_names,
            "Average Score": topic_scores
        })

        st.line_chart(chart_data.set_index("Topic"))
    else:
        st.write("No data to display yet")

    # ---------- STUDENT RANKING ----------
    st.subheader("Student Ranking")

    # Sort students by average (highest first)
    ranking_df = df.sort_values(by="Average", ascending=False).reset_index(drop=True)

    # Add rank column
    ranking_df["Rank"] = ranking_df.index + 1

    # Reorder columns
    ranking_df = ranking_df[["Rank", "Student", "Average"]]

    st.dataframe(ranking_df, use_container_width=True)

    # ---------- CLASS INSIGHT ----------
    st.subheader("Class Insight")

    # Collect topic scores
    topic_scores = {topic: [] for topic in TOPICS}

    for student in data:
        for topic in TOPICS:
            topic_scores[topic].extend(data[student][topic])

    # Calculate average per topic
    topic_avg = {
        topic: average(scores)
        for topic, scores in topic_scores.items()
        if scores
    }

    # Find weakest topic
    if topic_avg:
        weakest = min(topic_avg, key=topic_avg.get)
        st.info(f"Class is weakest in: {weakest}. Consider revising this topic.")

    # Find top student
    top_student = max(df.to_dict('records'), key=lambda x: x["Average"])
    st.success(f"Top student: {top_student['Student']} ({top_student['Average']})")

    # Count at-risk students
    at_risk_count = len(df[df["Average"] < 50])

    if at_risk_count > 0:
        st.warning(f"{at_risk_count} student(s) need attention.")
    else:
        st.success("No at-risk students")

else:
    st.write("Add students to begin")