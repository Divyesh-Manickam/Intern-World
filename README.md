# InternWorld – Internship & Placement Portal

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.1%2B-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()

InternWorld is a modern, production-grade internship and placement management web platform built primarily with **Python, Django, Django REST Framework, Bootstrap 5, and Chart.js**. It seamlessly unites **Students**, **Recruiters/Companies**, and **College Placement Administrators** in an integrated ecosystem with smart candidate matching, real-time application pipelines, automated interview management, analytics, and resume keyword extraction.

---

## 🌟 Key Highlights & Core Features

### 🎓 1. For Students
- **Smart Profile Builder**: Complete educational portfolio including Degree, Department, CGPA, graduation batch, projects, certifications, work experiences, and social handles.
- **Secure PDF Resume Upload & Keyword Extraction**: Strict PDF validation (format, header, MIME type, 5MB limit) with automated text parsing via `pypdf` for recommendation keyword matching.
- **Intelligent Recommendation Engine**: Modular compatibility scoring algorithm (0–100%) evaluating skills overlap, academic eligibility (degree & department), CGPA cutoffs, batch year, preferred locations, and target roles.
- **Real-Time Application Tracker**: Track applications across stages (`Applied`, `Under Review`, `Shortlisted`, `Interview Scheduled`, `Selected`, `Rejected`, `Withdrawn`).
- **Interactive Interview Hub**: View upcoming video meetings (Google Meet, Zoom, MS Teams) and on-site interview schedules with 1-click links.
- **Saved Opportunities (Bookmarks)**: Instant 1-click AJAX bookmarking of internships and placement roles.

### 🏢 2. For Recruiters & Employers
- **Company Branding & Verification**: Create and manage verified corporate profiles with company logos, descriptions, websites, and headquarters.
- **Opportunity Management**: Post internships and full-time placement listings with detailed eligibility criteria (min CGPA, branches, duration, stipends/salaries, and deadlines).
- **Candidate Pipeline & Multi-Filter Search**: Search and filter applicants by job posting, status, CGPA cutoffs, target skills, academic departments, and graduation years.
- **Candidate Evaluation & Private Notes**: Review full candidate dossiers, inspect PDF resumes, add internal notes, and update hiring statuses.
- **One-Click Interview Scheduling**: Schedule online video or in-person interviews directly from candidate cards with automated candidate notifications.

### 🛡️ 3. For College Placement Administrators
- **Executive Admin Center**: High-level platform telemetry with interactive Chart.js visualizations.
- **Company Verification Queue**: Review and verify new recruiter companies before live postings.
- **Opportunity Approval Workflow**: Audit and approve/reject job postings to ensure high quality.
- **User Account Governance**: Activate, deactivate, inspect, and monitor all student and recruiter accounts.
- **Deep Analytics & Insights**: Monthly application volume trends, hiring conversion funnel, and top in-demand technical skills across opportunities.

### 🚀 4. Django REST Framework (DRF) APIs
- Full RESTful endpoints under `/api/` with authentication, filtering, pagination, and serializers for mobile or headless frontend integration.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Python 3.12+, Django 5.1+, Django REST Framework |
| **Frontend UI** | Django Templates, HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons |
| **Data Visualization** | Chart.js 4.4+ |
| **PDF Extraction & Handling** | PyPDF (`pypdf`), Pillow (`PIL`) |
| **Database** | SQLite (Default for rapid local setup) / PostgreSQL ready |
| **Security & Auth** | Django Session Auth, PBKDF2 Password Hashing, CSRF Tokens, RBAC Mixins |

---

## 📂 Project Architecture

```
InternWorld/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/                 # Core project settings, URLs, error handlers
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/               # Custom User model, Role-Based Access Control, Auth
│   ├── models.py           # User model with STUDENT, RECRUITER, ADMIN roles
│   ├── forms.py            # Student & Recruiter registration, login forms
│   ├── views.py            # Auth views & role-specific redirection
│   ├── decorators.py       # @student_required, @recruiter_required, @admin_required
│   └── management/commands/seed_data.py # Comprehensive seed data command
│
├── students/               # Student profile, portfolio, resume management
│   ├── models.py           # StudentProfile, Project, Certification, Experience
│   ├── services.py         # PDF validator & pypdf text extractor
│   ├── forms.py            # Profile, Resume, and Portfolio forms
│   └── views.py            # Student dashboard, profile editor, bookmarks
│
├── recruiters/             # Company profiles, recruiter dashboard, applicant management
│   ├── models.py           # Company, RecruiterProfile
│   ├── forms.py            # Company branding & status update forms
│   └── views.py            # Recruiter dashboard, candidate evaluation
│
├── opportunities/          # Job & Internship postings, search & faceted filtering
│   ├── models.py           # Opportunity, SavedOpportunity
│   ├── filters.py          # DjangoFilterSet for faceted search
│   ├── forms.py            # Post & edit opportunity forms
│   └── views.py            # Public catalog, job details, recruiter management
│
├── applications/           # Application lifecycle, duplicate prevention, withdrawal
│   ├── models.py           # Application model with unique constraints
│   ├── forms.py            # Application submission form
│   └── views.py            # Application pipeline, status tracking
│
├── interviews/             # Meeting scheduling, agenda, video links
│   ├── models.py           # Interview model (Online, Offline, Phone)
│   ├── forms.py            # Interview scheduling form
│   └── views.py            # Upcoming and past interview views
│
├── notifications/          # Real-time in-app alerts and console email dispatch
│   ├── models.py           # Notification model
│   ├── services.py         # Notification dispatcher helper
│   └── context_processors.py # Navbar unread badge injector
│
├── recommendations/        # Modular candidate matching algorithm
│   ├── services.py         # Weighted compatibility engine (0-100%)
│   └── utils.py
│
├── analytics/              # Platform statistics and Chart.js feeds
│   ├── services.py         # Aggregation queries for trends and funnel
│   └── views.py            # Custom administrator dashboard & analytics
│
├── api/                    # Centralized Django REST Framework endpoints
│   ├── serializers.py      # Serializers for all models
│   ├── views.py            # ViewSets & APIViews
│   └── urls.py             # DRF DefaultRouter
│
├── static/                 # Stylesheets, JavaScript, Chart renderers
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       └── charts.js
│
├── media/                  # Uploaded PDF resumes and company logos
│   ├── resumes/
│   └── company_logos/
│
└── templates/              # Semantic Bootstrap 5 Django Templates
    ├── base.html
    ├── landing.html
    ├── about.html
    ├── components/
    ├── accounts/
    ├── students/
    ├── recruiters/
    ├── opportunities/
    ├── applications/
    ├── interviews/
    ├── notifications/
    ├── admin_dashboard/
    └── errors/
```

---

## 🚀 Quickstart & Installation

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone <repository-url>
cd InternWorld

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file (copied from `.env.example`):
```bash
cp .env.example .env
```
Default `.env` settings:
```env
SECRET_KEY=django-insecure-internworld-production-secret-key-change-in-prod-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 4. Run Migrations & Seed Sample Data
```bash
# Apply database schema
python manage.py makemigrations
python manage.py migrate

# Seed database with realistic demo accounts, opportunities, applications & interviews
python manage.py seed_data
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Demo User Accounts

All demo accounts are populated with realistic data via `python manage.py seed_data`:

| Role | Email | Password | Details |
|---|---|---|---|
| **Administrator** | `admin@example.com` | `Admin@12345` | Superuser with complete admin portal & Django admin access |
| **Student** | `student@example.com` | `Student@12345` | Aarav Sharma (NIT Trichy, B.Tech CSE, CGPA 8.85, PDF Resume uploaded) |
| **Recruiter** | `recruiter@example.com` | `Recruiter@12345` | Google Cloud India (Staff University Recruiter) |
| **Recruiter (MSFT)** | `microsoft.recruiter@example.com` | `Recruiter@12345` | Microsoft IDC (Campus Hiring Lead) |
| **Recruiter (TechCorp)** | `techcorp.recruiter@example.com` | `Recruiter@12345` | TechCorp AI Innovations (Head of People) |

---

## 🧪 Running Automated Tests

InternWorld includes a test suite covering registration, role-based view protections, opportunity approval, duplicate application prevention, recommendation scoring, and DRF REST APIs.

To execute all tests:
```bash
python manage.py test
```

---

## 📡 REST API Overview

Explore interactive API endpoints under `/api/`:

| Endpoint | Methods | Description |
|---|---|---|
| `/api/auth/user/` | `GET` | Retrieve currently authenticated user profile |
| `/api/opportunities/` | `GET` | List approved opportunities with search and filtering |
| `/api/opportunities/<id>/` | `GET` | Detailed opportunity metadata |
| `/api/students/profile/` | `GET` | Student profile details with portfolio & resume |
| `/api/recommendations/` | `GET` | Personalized opportunities for logged-in student |
| `/api/applications/` | `GET`, `POST` | Application submission & status management |
| `/api/interviews/` | `GET` | Scheduled interview sessions |
| `/api/notifications/` | `GET`, `POST` | Notification alerts & mark-all-read |
| `/api/admin/stats/` | `GET` | Platform-wide aggregation telemetry |

---

## 🔒 Security Best Practices Implemented

- **Password Security**: Strong PBKDF2 hashing algorithm via Django auth framework.
- **CSRF & XSS Protection**: Strict CSRF tokens on all POST/PUT/DELETE forms and AJAX requests.
- **PDF Upload Hardening**: Multi-layered validation checking `.pdf` extensions, MIME types, file size limits (5MB), and PDF magic bytes (`%PDF-`).
- **Database Integrity**: Composite database uniqueness constraint on `('student', 'opportunity')` preventing race-condition duplicate applications.
- **Role Isolation**: Strict decorators (`@student_required`, `@recruiter_required`, `@admin_required`) and mixins preventing cross-role privilege escalation.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
