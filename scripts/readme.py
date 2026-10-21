"""Generate README.md so every image gets matching dark and light <picture> sources.

    python scripts/readme.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = "https://github.com/Prashasthi-18/"
OUTPUT = "https://raw.githubusercontent.com/Prashasthi-18/Prashasthi-18/output/"


def pic(name, alt, width="100%", base="./assets/"):
    w = f' width="{width}"' if width else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}{name}.svg"/>'
            f'<source media="(prefers-color-scheme: light)" srcset="{base}{name}-light.svg"/>'
            f'<img src="{base}{name}.svg" alt="{alt}"{w}/></picture>')


def center(*items):
    return '<p align="center">\n  ' + "\n  ".join(items) + "\n</p>"


def link(href, inner):
    return f'<a href="{href}">{inner}</a>'


def header(key, alt):
    return center(pic(f"h-{key}", alt))


def cards(items):
    return center(*[link(GH + repo, pic(f"card-{key}", alt, "49%")) for key, repo, alt in items])


BUTTONS = center(
    link("https://portfolio-rho-silk-72.vercel.app", pic("btn-portfolio", "Portfolio", None)),
    link("https://www.linkedin.com/in/prashasthiboin/", pic("btn-linkedin", "LinkedIn", None)),
    link("mailto:boinprashasthi@gmail.com", pic("btn-email", "Email me", None)),
)

# Kept exactly as before.
SNAKE = """<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Prashasthi-18/Prashasthi-18/output/github-contribution-grid-snake-dark.svg"/>
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Prashasthi-18/Prashasthi-18/output/github-contribution-grid-snake.svg"/>
    <img alt="Contribution snake" src="https://raw.githubusercontent.com/Prashasthi-18/Prashasthi-18/output/github-contribution-grid-snake-dark.svg"/>
  </picture>
</p>"""

README = f"""{center(pic('hero', 'Boin Prashasthi. Software Engineer: Backend and APIs, Full-stack, Generative AI. Software Development Intern at FlyingDuck.'))}

{BUTTONS}

{header('about', 'About me')}

{center(pic('about', 'about.py: Software Development Intern at FlyingDuck; B.Tech CSE (Cyber Security), VNR VJIET, CGPA 9.15; Hyderabad, India; focus: backend, REST APIs, full-stack, generative AI, DevOps'))}

Driven by curiosity and a strong interest in software development, I enjoy understanding how systems work and turning ideas into reliable, useful applications. I learn by building: backend services and APIs, full-stack apps, and AI features that hold up in real use.

- **Backend & APIs:** services and REST APIs with FastAPI, Flask, Node.js and Express.js
- **Full-stack:** interactive frontends wired to Python backends, containerised with Docker
- **Generative AI:** multi-agent systems, RAG and LLM workflows with LangChain and LangGraph
- **Testing & DevOps:** pytest, Playwright, GitHub Actions and GitLab CI/CD
- **Security:** Cyber Security major and CTF winner
- **Product:** I write PRDs and product teardowns, and design software around real users

{center(pic('pipeline', 'How I build: Design, Build, Integrate, Test, Ship'))}

{header('experience', 'Experience and education')}

**Software Development Intern** · FlyingDuck · *Aug 2026 – Present*
- Contributing to application development through feature implementation, debugging, testing and engineering workflows
- Built a **[Dependency Upgrade Impact Analyzer]({GH}Dependency-Upgrade-Analyzer-Advanced)**: give it a PyPI or npm package and two versions, and it walks every release in between, merges the official release notes and changelogs, and flags breaking changes and known security advisories in one report
- Worked on **license analysis** for software dependencies
- Working with version control, code maintenance and collaborative development practices

**Generative AI Engineer Intern** · BlackBucks · *Jun 2026 – Jul 2026*
- Developed backend applications and APIs with Python and FastAPI for AI-powered software systems
- Built application workflows involving data processing, API integration and model-powered features
- Worked on evaluation, debugging, deployment workflows and scalable application development

| Degree | Institution | Years | Score |
|---|---|---|---|
| **B.Tech, Computer Science and Engineering (Cyber Security)** | VNR VJIET | 2024 – Present | CGPA **9.15** / 10 |
| **Intermediate** | Page Junior College | 2022 – 2024 | **98.6%** |

{header('projects', 'Software engineering projects')}

{cards([
    ('analyzer', 'Dependency-Upgrade-Analyzer-Advanced', 'Dependency Upgrade Impact Analyzer'),
    ('gateway', 'API-Gateway', 'API Gateway and Rate Limiter'),
    ('req2test', 'Req2Test', 'Req2Test Crew'),
    ('voice', 'AI-Voice-Assistant', 'AI Voice Assistant'),
    ('pipeline', 'Automated-Code-Testing-Pipeline', 'Automated Code Testing Pipeline'),
    ('pricepulse', 'Price-Pulse-Compare-Prices-Instantly', 'Price Pulse'),
])}

{header('ai', 'AI and LLM applications')}

{cards([
    ('llmops', 'LLMOPS', 'LLMOps Multi-Agent Platform'),
    ('video', 'AI-Video-Assistant-With-RAG', 'AI Video Assistant with RAG'),
    ('clearpay', 'ClearPAY', 'ClearPay'),
    ('apitest', 'API-Testing-Agent', 'AI API Testing Agent'),
    ('research', 'Multi-Agent-AI-Reasearch-System', 'Multi-Agent Research System'),
    ('guardrails', 'Guardrails-Mini-Project', 'Healthcare Guardrails Assistant'),
])}

<p align="center"><sub>Try the <a href="https://ai-video-assistant-with-rag-enhylzyarkuexzqkhky3hc.streamlit.app/">AI Video Assistant live demo</a> · rate limiter internals in <a href="{GH}Rate_Limiter_Project">Rate_Limiter_Project</a></sub></p>

<details>
<summary><b>More projects</b></summary>
<br/>

| Project | What it does | Stack |
|---|---|---|
| [Patient Discharge Planner]({GH}AI-Assisted-Patient-Discharge-Readiness-and-Follow-Up-Planner) | Clinical decision-support prototype for discharge readiness and follow-ups (synthetic data only) | Python, LLMs |
| [ClearAI]({GH}CLEARAI) | Customs-clearance prototype: document analysis, risk score, auto-filled declaration | React, Vite |
| [Enterprise RAG]({GH}Enterprise-RAG) · [RAG]({GH}RAG) | Retrieval-augmented generation pipelines | LangChain |
| [Resume Builder]({GH}Resume-builder-with-templates) | Resume builder with templates | Web |
| Swiggy product case study | Product teardown with PRDs, user-journey analysis and RICE prioritisation | Notion |

</details>

{header('skills', 'Technical skills')}

{center(pic('skills', 'Technical skills, as layers a request passes through. Languages: Python, Java, C, C++, SQL, JavaScript. Backend and APIs: FastAPI, Flask, Node.js, Express.js, REST APIs, JWT, OAuth, Server-Sent Events. Data: PostgreSQL, SQLite, ChromaDB, Pandas, NumPy, scikit-learn. AI and LLMs: LangChain, LangGraph, CrewAI, RAG, multi-agent systems, guardrails. Ship and test: Docker, Linux, Git, GitHub Actions, GitLab CI/CD, pytest, Playwright'))}

<details>
<summary><b>Skills as text</b></summary>
<br/>

| Area | Skills |
|---|---|
| **Languages** | Python, Java, C, C++, SQL, JavaScript |
| **Backend** | FastAPI, Flask, Node.js, Express.js, REST APIs |
| **Frontend** | HTML, CSS, Streamlit |
| **Databases** | PostgreSQL, SQLite, ChromaDB |
| **Development** | Git, GitHub, Docker, Linux, VS Code, API development, debugging, testing |
| **Testing & CI/CD** | pytest, Playwright, GitHub Actions, GitLab CI/CD |
| **AI / ML** | LangChain, LangGraph, CrewAI, Generative AI, RAG, multi-agent systems, machine learning, Pandas, NumPy, scikit-learn |

</details>

{header('achievements', 'Achievements and certifications')}

{center(pic('achievements', 'Winner of the GDGC Room Style CTF; 25+ hackathons; 7+ Capture the Flag competitions; CGPA 9.15'))}

| Certification | Issuer |
|---|---|
| Generative AI Leader | Google Cloud |
| Agentic AI using LangChain, LangGraph, CrewAI & AutoGen | IBM SkillsBuild |
| Introduction to Generative AI | IBM SkillsBuild |
| GitLab CI/CD Pipelines for Beginners | Udemy |
| What is Product Management? | Simplilearn |

I've also published product management case studies on Notion.

{header('activity', 'GitHub activity')}

{center(pic('stats', 'GitHub activity: contributions, streaks and most used languages', base=OUTPUT))}

{SNAKE}

{header('connect', "Let's connect")}

<p align="center">I'm always happy to talk about backend engineering, APIs, AI systems, security or product ideas, and to team up on projects and hackathons.</p>

{BUTTONS}

{center(pic('footer', "Let's build something reliable."))}
"""

if __name__ == "__main__":
    (ROOT / "README.md").write_text(README, encoding="utf-8")
    print("wrote README.md")
