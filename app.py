import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import csv
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader
import re
import os

from database import save_candidate, get_candidates, get_dashboard_data,update_candidate,delete_candidate



# ---------------- PDF TEXT ----------------

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


# ---------------- RESUME DETAILS ----------------

def extract_resume_data(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(
        r'(?:\+91[\s-]?)?[6-9]\d{9}',
        text
    )
    phone = phone_match.group(0) if phone_match else ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    name = "Unknown"

    # First few lines me name dhundhna
    for line in lines[:10]:
        clean_line = line.strip()

        if (
            "@" not in clean_line
            and not re.search(r'\d', clean_line)
            and 1 < len(clean_line.split()) <= 4
            and clean_line.lower() not in [
                "resume",
                "curriculum vitae",
                "cv"
            ]
        ):
            name = clean_line
            break

    # Agar name nahi mila to filename se
    if name == "Unknown":
        filename = os.path.basename(pdf_path)
        name = os.path.splitext(filename)[0]
        name = name.replace("_", " ").replace("-", " ")

    education = "Not Found"

    education_patterns = [
        r'\bB\.?Tech\b',
        r'\bBCA\b',
        r'\bMCA\b',
        r'\bM\.?Tech\b',
        r'\bMBA\b',
        r'\bB\.?Sc\b',
        r'\bM\.?Sc\b',
        r'\bB\.?A\b',
        r'\bM\.?A\b'
    ]

    for pattern in education_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            education = match.group(0)
            break

    experience = "Fresher"

    experience_match = re.search(
        r'experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
        text,
        re.IGNORECASE
    )

    if experience_match:
        experience = experience_match.group(1) + " years"
    elif re.search(r'\bfresher\b|\bfresh graduate\b', text, re.IGNORECASE):
        experience = "Fresher"
    return name, email, phone,education,experience


# ---------------- SELECT RESUME ----------------

def select_resume():
    file_path = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if file_path:
        selected_file.set(file_path)
        resume_label.config(
            text=os.path.basename(file_path)
        )


# ---------------- SCREEN RESUME ----------------

def screen_resume():

    file_path = selected_file.get()

    if not file_path:
        messagebox.showwarning(
            "Warning",
            "Please select a resume first"
        )
        return

    resume_text = extract_text_from_pdf(file_path)

    if not resume_text.strip():
        messagebox.showerror(
            "Error",
            "Resume text could not be extracted."
        )
        return

    # Required skills
    required_skills = [
        "Python",
        "MySQL",
        "Excel",
        "Pandas",
        "Power BI"
    ]

    # Find matched skills
    matched_skills = []

    for skill in required_skills:
        if skill.lower() in resume_text.lower():
            matched_skills.append(skill)

    # Score
    score = (
        len(matched_skills) /
        len(required_skills)
    ) * 100

    # Status
    if score >= 70:
        status = "Shortlisted"
    else:
        status = "Rejected"

    # Candidate details
    name, email, phone,education,experience = extract_resume_data(file_path)

    # Save to database
    save_candidate(
        name=name,
        email=email,
        phone=phone,
        skills=", ".join(matched_skills),
        education=education,
        experience=experience,
        score=score,
        status=status
    )

    # Show result
    result_label.config(
        text=
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Matched Skills: {', '.join(matched_skills)}\n"
        f"Match Score: {score:.0f}%\n"
        f"Status: {status}"
    )

    messagebox.showinfo(
        "Success",
        "Candidate screened and saved successfully!"
    )


# ---------------- VIEW CANDIDATES ----------------
def view_candidates():

    file_path = selected_file.get()

    window = tk.Toplevel(root)
    window.title("View Candidates")
    window.geometry("800x500")

    title = tk.Label(
        window,
        text="Candidate List",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    if not file_path:
        tk.Label(
            window,
            text="Please select and screen a resume first."
        ).pack(pady=20)
        return

    # Selected resume se email aur phone nikalo
    name, email, phone, education, experience = extract_resume_data(file_path)

    # Database ke candidates lao
    all_candidates = get_candidates()

    # Sirf selected resume wala candidate
    candidates = [
        candidate
        for candidate in all_candidates
        if candidate[1] == email or candidate[2] == phone
    ]

    if not candidates:
        tk.Label(
            window,
            text="This resume has not been screened yet."
        ).pack(pady=20)
        return

    for candidate in candidates:

        text = (
            f"Name: {candidate[0]}\n"
            f"Email: {candidate[1]}\n"
            f"Phone: {candidate[2]}\n"
            f"Skills: {candidate[3]}\n"
            f"Education: {candidate[4]}\n"
            f"Experience: {candidate[5]}\n"
            f"Score: {candidate[6]}%\n"
            f"Status: {candidate[7]}"
        )

        tk.Label(
            window,
            text=text,
            justify="left",
            anchor="w",
            relief="solid",
            padx=10,
            pady=10
        ).pack(
            fill="x",
            padx=20,
            pady=5
        )


def edit_candidate():
    candidates = get_candidates()

    if not candidates:
        messagebox.showinfo("Update", "No candidates found.")
        return

    window = tk.Toplevel(root)
    window.title("Update Candidate")
    window.geometry("500x600")

    tk.Label(
        window,
        text="Update Candidate",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    tk.Label(window, text="Candidate ID").pack()
    id_entry = tk.Entry(window, width=40)
    id_entry.pack(pady=5)

    tk.Label(window, text="Name").pack()
    name_entry = tk.Entry(window, width=40)
    name_entry.pack(pady=5)

    tk.Label(window, text="Email").pack()
    email_entry = tk.Entry(window, width=40)
    email_entry.pack(pady=5)

    tk.Label(window, text="Phone").pack()
    phone_entry = tk.Entry(window, width=40)
    phone_entry.pack(pady=5)

    tk.Label(window, text="Skills").pack()
    skills_entry = tk.Entry(window, width=40)
    skills_entry.pack(pady=5)

    tk.Label(window, text="Education").pack()
    education_entry = tk.Entry(window, width=40)
    education_entry.pack(pady=5)

    tk.Label(window, text="Experience").pack()
    experience_entry = tk.Entry(window, width=40)
    experience_entry.pack(pady=5)

    def update_data():
        update_candidate(
            id_entry.get(),
            name_entry.get(),
            email_entry.get(),
            phone_entry.get(),
            skills_entry.get(),
            education_entry.get(),
            experience_entry.get()
        )

        messagebox.showinfo(
            "Success",
            "Candidate updated successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="Update Candidate",
        command=update_data,
        width=25
    ).pack(pady=20)


def search_candidates():

    candidates = get_candidates()

    window = tk.Toplevel(root)
    window.title("Search Candidates")
    window.geometry("800x600")

    tk.Label(
        window,
        text="Search Candidates",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    search_var = tk.StringVar()

    search_entry = tk.Entry(
        window,
        textvariable=search_var,
        width=50
    )
    search_entry.pack(pady=5)

    tk.Label(
        window,
        text="Search by Name, Email, Skill or Status"
    ).pack()

    result_frame = tk.Frame(window)
    result_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def show_results():

        for widget in result_frame.winfo_children():
            widget.destroy()

        keyword = search_var.get().lower().strip()

        for candidate in candidates:

            searchable_text = " ".join([
                str(candidate[0]),
                str(candidate[1]),
                str(candidate[3]),
                str(candidate[7])
            ]).lower()

            if keyword in searchable_text:

                text = (
                    f"Name: {candidate[0]}\n"
                    f"Email: {candidate[1]}\n"
                    f"Phone: {candidate[2]}\n"
                    f"Skills: {candidate[3]}\n"
                    f"Education: {candidate[4]}\n"
                    f"Experience: {candidate[5]}\n"
                    f"Score: {candidate[6]}%\n"
                    f"Status: {candidate[7]}"
                )

                tk.Label(
                    result_frame,
                    text=text,
                    justify="left",
                    anchor="w",
                    relief="solid",
                    padx=10,
                    pady=10
                ).pack(
                    fill="x",
                    pady=5
                )

    tk.Button(
        window,
        text="Search",
        command=show_results,
        width=20
    ).pack(pady=10)



def export_candidates():

    candidates = get_candidates()

    if not candidates:
        messagebox.showinfo(
            "Export",
            "No candidates found."
        )
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")]
    )

    if not file_path:
        return

    with open(file_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Name",
            "Email",
            "Phone",
            "Skills",
            "Education",
            "Experience",
            "Match Score",
            "Status"
        ])

        for candidate in candidates:
            writer.writerow(candidate)

    messagebox.showinfo(
        "Export Successful",
        "Candidates exported successfully!"
    )



def remove_candidate():

    candidates = get_candidates()

    if not candidates:
        messagebox.showinfo("Delete", "No candidates found.")
        return

    window = tk.Toplevel(root)
    window.title("Delete Candidate")
    window.geometry("400x250")

    tk.Label(
        window,
        text="Delete Candidate",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(window, text="Candidate ID").pack()

    id_entry = tk.Entry(window, width=30)
    id_entry.pack(pady=10)

    def delete_data():

        candidate_id = id_entry.get().strip()

        if not candidate_id:
            messagebox.showwarning(
                "Warning",
                "Please enter Candidate ID."
            )
            return

        delete_candidate(candidate_id)

        messagebox.showinfo(
            "Success",
            "Candidate deleted successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="Delete Candidate",
        command=delete_data,
        width=20
    ).pack(pady=20)
# ---------------- DASHBOARD ----------------

# ---------------- DASHBOARD ----------------

def dashboard():

    data = get_dashboard_data()

    window = tk.Toplevel(root)
    window.title("Dashboard")
    window.geometry("650x600")

    tk.Label(
        window,
        text="Dashboard",
        font=("Arial", 22, "bold")
    ).pack(pady=20)

    tk.Label(
        window,
        text=f"Total Candidates: {data[0]}",
        font=("Arial", 14)
    ).pack(pady=5)

    tk.Label(
        window,
        text=f"Shortlisted: {data[1]}",
        font=("Arial", 14)
    ).pack(pady=5)

    tk.Label(
        window,
        text=f"Rejected: {data[2]}",
        font=("Arial", 14)
    ).pack(pady=5)

    tk.Label(
        window,
        text=f"Average Match Score: {data[3]:.0f}%",
        font=("Arial", 14)
    ).pack(pady=5)

    # Chart
    fig, ax = plt.subplots(figsize=(5, 3.5))

    labels = ["Shortlisted", "Rejected"]
    values = [data[1], data[2]]

    ax.bar(labels, values)
    ax.set_title("Candidate Status")
    ax.set_ylabel("Number of Candidates")

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()


root.title("AI-Based Resume Screening System")
root.geometry("650x850")
root.resizable(False, False)
root.configure(bg="#f2f4f7")
selected_file = tk.StringVar()

title_label = tk.Label(
    root,
    text="AI-Based Resume Screening System",
    font=("Arial", 22, "bold"),
    bg="#f2f4f7"
)

title_label.pack(pady=25)

resume_label = tk.Label(
    root,
    text="No resume selected",
    font=("Arial", 11,"italic"),
    bg="#f2f4f7"
)
resume_label.pack(pady=10)

select_button = tk.Button(
    root,
    text="Select Resume PDF",
    command=select_resume,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#4CAF50",
    fg="white"
)

screen_button = tk.Button(
    root,
    text="Screen Resume",
    command=screen_resume,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#2196F3",
    fg="white"
)
select_button.pack(pady=10)
screen_button.pack(pady=10)

view_button = tk.Button(
    root,
    text="View Candidates",
    command=view_candidates,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#9C27B0",
    fg="white"
)

view_button.pack(pady=10)
dashboard_button = tk.Button(
    root,
    text="Dashboard",
    command=dashboard,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#FF9800",
    fg="white"
)

dashboard_button.pack(pady=10)
result_label = tk.Label(
    root,
    text="",
    font=("Arial", 11,"bold"),
    justify="left",
    bg="#f2f4f7"
)
result_label.pack(pady=20)
search_button = tk.Button(
    root,
    text="Search Candidates",
    command=search_candidates,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#607D8B",
    fg="white"
)

search_button.pack(pady=10)

export_button = tk.Button(
    root,
    text="Export Candidates",
    command=export_candidates,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#009688",
    fg="white"
)

export_button.pack(pady=10)
update_button = tk.Button(
    root,
    text="Update Candidate",
    command=edit_candidate,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#795548",
    fg="white"
)

update_button.pack(pady=10)

delete_button = tk.Button(
    root,
    text="Delete Candidate",
    command=remove_candidate,
    width=25,
    height=2,
    font=("Arial", 11, "bold"),
    bg="#F44336",
    fg="white"
)

delete_button.pack(pady=10)
root.mainloop()
