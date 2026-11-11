# 🌐 DataSphere — Discover Your Skills. Shape Your Future.

**DataSphere** is an AI-powered career guidance and skill development platform designed to help students understand their current skills, identify gaps, explore career pathways, and build a structured learning journey.

By combining skill-gap analysis, personalized roadmaps, AI-generated project challenges, and progress tracking, DataSphere helps learners move from knowing their skills to developing them.

---

## ✨ Key Features

### 👤 User Authentication
- Secure account registration and login.
- Email verification through Supabase Authentication.
- Individual user accounts.
- Secure session management.

### 📊 Skill Gap Analysis
- Compare existing skills against a selected career role.
- Identify matched, partially matched, and missing skills.
- Highlight priority skill gaps.
- View skill coverage and category-wise analysis.

### 🧭 Personalized Learning Roadmaps
- AI-powered learning recommendations using Google Gemini.
- Structured learning guidance based on skill gaps.
- Fallback recommendations when AI services are unavailable.

### 💡 AI Project Challenges
- Generate practical project ideas based on learning needs.
- Explore project descriptions and required skills.
- Add projects to the personal progress tracker.

### 📈 Progress Tracking
- Track practiced skills.
- Manage project progress.
- Record learning hours and notes.
- Monitor completed projects.

### 📄 Downloadable Reports
- Generate personalized skill development reports.
- Review skill analysis and progress.
- Download reports in Markdown format.

### ☁️ Cloud Database
- Supabase PostgreSQL database.
- Persistent profile and learning progress storage.
- Row Level Security (RLS) for user data protection.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web application |
| Pandas | Data processing |
| Google Gemini API | AI-powered recommendations and project generation |
| Supabase | Authentication and cloud database |
| PostgreSQL | Persistent data storage |
| Git & GitHub | Version control and collaboration |
| Streamlit Community Cloud | Application deployment |

---

## 📁 Project Structure

```text
Build-With-Google/
│
├── app.py
│
├── data/
│   ├── roles_skills.csv
│   └── skills_catalog.csv
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── skill_matcher.py
│   ├── roadmap_builder.py
│   ├── gemini_service.py
│   ├── fallback_content.py
│   ├── progress_tracker.py
│   ├── profile_service.py
│   ├── tracker_service.py
│   ├── supabase_client.py
│   ├── report.py
│   └── ui_components.py
│
├── views/
│   ├── landing.py
│   ├── profile.py
│   ├── dashboard.py
│   ├── skill_gap.py
│   ├── roadmap.py
│   ├── projects.py
│   ├── tracker.py
│   └── report_view.py
│
├── assets/
├── tests/
├── scripts/
│
├── .streamlit/
│   └── secrets.toml
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Maheen3653/Build-With-Google.git
cd Build-With-Google
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure API Credentials

Create a folder named `.streamlit` in the project root.

Inside it, create `secrets.toml`.

Add the following configuration:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"

SUPABASE_KEY = "YOUR_SUPABASE_PUBLISHABLE_KEY"
```

Replace the placeholders with your actual credentials.

**Important:** Never commit `secrets.toml` or expose API credentials publicly.

### 5. Run the Application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

## 🔐 Supabase Configuration

DataSphere uses Supabase for authentication and persistent user data.

The database includes:

- `profiles`
- `practised_skills`
- `user_projects`
- `learning_logs`

Security features include:

- Supabase Authentication.
- Email verification.
- Row Level Security (RLS).
- User-specific database access policies.

Each user accesses their own records through authenticated database operations.

To use an existing DataSphere Supabase project, configure its Project URL and Publishable Key in your environment secrets.

---

## 🤖 Google Gemini Integration

Google Gemini powers the AI-assisted learning experience.

It supports:
- Personalized learning guidance.
- Roadmap generation.
- Practical project recommendations.
- AI-assisted skill development suggestions.

A valid Gemini API key is required.

DataSphere also includes fallback content for situations where AI services are temporarily unavailable.

---

## ☁️ Deployment

DataSphere can be deployed using **Streamlit Community Cloud**.

1. Push the project to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect the GitHub repository.
4. Select the `main` branch.
5. Set the main file path to `app.py`.
6. Deploy the application.
7. Add Gemini and Supabase credentials under the application's **Settings → Secrets**.

Local secrets are not automatically transferred to Streamlit Cloud.

---

## 📌 Data and Methodology Disclaimer

The included career-role and skill datasets are illustrative demonstration data.

Skill matching and coverage calculations are intended to support learning and self-assessment. They should not be interpreted as verified job-market requirements, professional certification, or guaranteed employment readiness.

AI-generated recommendations should be reviewed and adapted to individual learning needs.

---

## 🔒 Security

- API credentials are stored outside the source code.
- `.streamlit/secrets.toml` must remain excluded from Git.
- Supabase Publishable Keys are used for client-side authenticated access.
- Database access is restricted through Row Level Security.
- Never expose Supabase Secret or service-role keys.

---

## 🚀 Future Improvements

Potential future enhancements include:

- More comprehensive verified career datasets.
- Advanced analytics and learning insights.
- Additional career pathways.
- Enhanced roadmap customization.
- More project-based learning challenges.
- Improved progress visualization.

---

## 👩‍💻 Project Team

**DataSphere — Build With Google**

Developed as a collaborative project focused on combining artificial intelligence, data science, and personalized learning.

---

### Discover your skills. Identify your gaps. Build your future.

**DataSphere — Your journey towards smarter skill development starts here.**