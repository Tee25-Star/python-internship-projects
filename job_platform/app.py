"""
Online Recruitment / Job Application Platform
A visually stunning Flask web application for job seekers and employers.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Sample job data (in production, this would come from a database)
JOBS = [
    {
        "id": 1,
        "title": "Senior Software Engineer",
        "company": "TechNova Inc.",
        "location": "San Francisco, CA (Remote)",
        "type": "Full-time",
        "salary": "$140k - $180k",
        "posted": "2025-01-28",
        "description": "We're looking for a Senior Software Engineer to lead our core platform team. You'll architect scalable systems, mentor engineers, and drive technical excellence.",
        "requirements": ["5+ years Python/Go experience", "Distributed systems", "AWS/GCP", "Strong communication"],
        "logo": "💻",
    },
    {
        "id": 2,
        "title": "Product Designer",
        "company": "Design Studio Co.",
        "location": "New York, NY (Hybrid)",
        "type": "Full-time",
        "salary": "$95k - $125k",
        "posted": "2025-01-30",
        "description": "Join our design team to create beautiful, user-centered products. You'll own the design process from research to high-fidelity prototypes.",
        "requirements": ["Figma expert", "3+ years product design", "Portfolio required", "User research"],
        "logo": "🎨",
    },
    {
        "id": 3,
        "title": "Data Scientist",
        "company": "DataFlow Analytics",
        "location": "Austin, TX (Remote)",
        "type": "Full-time",
        "salary": "$120k - $155k",
        "posted": "2025-02-01",
        "description": "Help us turn data into decisions. You'll build ML models, design experiments, and work with engineering to ship impact at scale.",
        "requirements": ["Python, SQL, PyTorch/TensorFlow", "A/B testing", "PhD or 4+ years experience"],
        "logo": "📊",
    },
    {
        "id": 4,
        "title": "DevOps Engineer",
        "company": "CloudScale",
        "location": "Seattle, WA (On-site)",
        "type": "Full-time",
        "salary": "$130k - $165k",
        "posted": "2025-01-29",
        "description": "Own our CI/CD pipelines and cloud infrastructure. You'll ensure reliability, security, and performance for millions of users.",
        "requirements": ["Kubernetes, Terraform", "AWS/Azure", "5+ years DevOps", "On-call rotation"],
        "logo": "⚙️",
    },
    {
        "id": 5,
        "title": "Frontend Developer",
        "company": "WebCraft Labs",
        "location": "Berlin, Germany (Remote)",
        "type": "Contract",
        "salary": "€70 - €90/hour",
        "posted": "2025-02-02",
        "description": "Build stunning, performant web applications with React and TypeScript. Work with a distributed team on greenfield projects.",
        "requirements": ["React, TypeScript", "CSS/Sass", "REST/GraphQL", "English fluent"],
        "logo": "🌐",
    },
    {
        "id": 6,
        "title": "Marketing Manager",
        "company": "Growth Partners",
        "location": "Chicago, IL (Hybrid)",
        "type": "Full-time",
        "salary": "$85k - $110k",
        "posted": "2025-01-27",
        "description": "Lead our B2B marketing strategy. You'll own campaigns, content, and analytics to drive pipeline and brand awareness.",
        "requirements": ["5+ years B2B marketing", "HubSpot/Salesforce", "Content strategy", "Team leadership"],
        "logo": "📈",
    },
]

APPLICATIONS = []  # In-memory store for demo; use DB in production


def get_job_by_id(job_id):
    return next((j for j in JOBS if j["id"] == job_id), None)


@app.route("/")
def index():
    return render_template("index.html", jobs=JOBS)


@app.route("/jobs")
def jobs_list():
    query = request.args.get("q", "").lower()
    job_type = request.args.get("type", "")
    location = request.args.get("location", "").lower()
    filtered = JOBS
    if query:
        filtered = [
            j
            for j in filtered
            if query in j["title"].lower()
            or query in j["company"].lower()
            or query in " ".join(j["requirements"]).lower()
        ]
    if job_type:
        filtered = [j for j in filtered if j["type"].lower() == job_type.lower()]
    if location:
        filtered = [j for j in filtered if location in j["location"].lower()]
    return render_template("jobs.html", jobs=filtered, search_query=query, filters={"type": job_type, "location": location})


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = get_job_by_id(job_id)
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for("jobs_list"))
    return render_template("job_detail.html", job=job)


@app.route("/jobs/<int:job_id>/apply", methods=["GET", "POST"])
def apply(job_id):
    job = get_job_by_id(job_id)
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for("jobs_list"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        resume = request.form.get("resume", "").strip()
        cover = request.form.get("cover_letter", "").strip()
        if not name or not email:
            flash("Please provide your name and email.", "error")
            return render_template("apply.html", job=job)
        APPLICATIONS.append(
            {
                "job_id": job_id,
                "job_title": job["title"],
                "company": job["company"],
                "name": name,
                "email": email,
                "resume": resume,
                "cover_letter": cover,
                "applied_at": datetime.now().isoformat(),
            }
        )
        flash(f"Application submitted for {job['title']} at {job['company']}. Good luck!", "success")
        return redirect(url_for("job_detail", job_id=job_id))
    return render_template("apply.html", job=job)


@app.route("/applications")
def applications_list():
    return render_template("applications.html", applications=APPLICATIONS)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
