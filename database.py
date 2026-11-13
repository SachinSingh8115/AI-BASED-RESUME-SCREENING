import os
from dotenv import load_dotenv

load_dotenv()
import mysql.connector

def save_candidate(name, email, phone, skills, education, experience, score, status):

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="resume_screening"
    )

    cursor = connection.cursor()

    # Check if candidate already exists
    check_query = """
    SELECT candidate_id
    FROM candidates
    WHERE email = %s AND phone = %s
    """

    cursor.execute(check_query, (email, phone))
    existing = cursor.fetchone()

    if existing:
        # Update existing candidate
        update_query = """
        UPDATE candidates
        SET name=%s,
            skills=%s,
            education=%s,
            experience=%s,
            match_score=%s,
            status=%s
        WHERE candidate_id=%s
        """

        values = (
            name,
            skills,
            education,
            experience,
            score,
            status,
            existing[0]
        )

        cursor.execute(update_query, values)

    else:
        # Insert new candidate
        insert_query = """
        INSERT INTO candidates
        (name, email, phone, skills, education, experience, match_score, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            phone,
            skills,
            education,
            experience,
            score,
            status
        )

        cursor.execute(insert_query, values)

    connection.commit()

    cursor.close()
    connection.close()

    print("Candidate saved successfully!")

def update_candidate(candidate_id, name, email, phone, skills, education, experience):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="resume_screening"
    )

    cursor = connection.cursor()

    query = """
    UPDATE candidates
    SET name=%s,
        email=%s,
        phone=%s,
        skills=%s,
        education=%s,
        experience=%s
    WHERE candidate_id=%s
    """

    values = (
        name,
        email,
        phone,
        skills,
        education,
        experience,
        candidate_id
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

def delete_candidate(candidate_id):

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="resume_screening"
    )

    cursor = connection.cursor()

    query = "DELETE FROM candidates WHERE candidate_id=%s"

    cursor.execute(query, (candidate_id,))

    connection.commit()

    cursor.close()
    connection.close()

    print("Candidate deleted successfully!")


def get_candidates():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="resume_screening"
    )
    cursor = connection.cursor()
    cursor.execute("""
    select name,email,phone,skills,education,experience,match_score,status from candidates""")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data
def get_dashboard_data():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="resume_screening"
    )

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM candidates WHERE status='Shortlisted'"
    )
    shortlisted = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM candidates WHERE status='Rejected'"
    )
    rejected = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(match_score) FROM candidates"
    )
    average_score = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return total, shortlisted, rejected, average_score