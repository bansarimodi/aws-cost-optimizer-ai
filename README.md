# ☁️ AWS Cost Optimization using Agentic AI (LangGraph)

This project is an interactive AI-powered dashboard that helps identify and remove idle or unused AWS resources using LangGraph agents. The system is designed with human-in-the-loop feedback for safer decision-making and cloud cost efficiency.

## 🚀 Features

- 🔐 Secure AWS Credential Input
- 🤖 LLM-powered idle resource detection (EC2, S3, Snapshots)
- 👁️ Human feedback verification before deletion
- 🗑️ Resource deletion automation using boto3
- 📊 Interactive Streamlit UI
- 🌐 Modular LangGraph-based multi-agent system

---

## 🧠 How It Works

1. **User Inputs AWS Credentials** through a secure UI.
2. **Idle Resource Detection Agent** scans EC2, S3, and Snapshots:
   - EC2: stopped > 7 days
   - S3: empty and not prefixed with prod/logs/backup
   - Snapshots: older than 30 days
3. **Human Feedback Agent** asks if user approves deletion.
4. **Deletion Agent** removes selected AWS resources upon approval.

---

## 🗂️ Project Structure

```
.
├── .env                  # API keys (Groq)
├── main.py               # Streamlit app frontend
├── agents.py             # Core AI agents (detection, feedback, deletion)
├── aws_connector.py      # AWS SDK wrapper functions
├── graph_state.py        # LangGraph workflow configuration
├── requirements.txt      # Python dependencies
```

---

## 🛠️ Installation

1. **Clone this repo**:
   ```bash
   git clone https://github.com/your-username/aws-cost-ai.git
   cd aws-cost-ai
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Groq API Key** in `.env`:
   ```
   GROQ_API_KEY="your_groq_api_key_here"
   ```

---

## ▶️ Run the App

```bash
streamlit run main.py
```

---

## 🔐 Notes on Security

- AWS credentials are **not stored**—used only in session memory.
- Make sure to **never commit `.env`** to version control.
- Supports scanning and deletion for **your AWS-owned resources** only (via `OwnerIds=['self']` in snapshots).

---

## 📚 Tech Stack

- **LangGraph**: LLM-powered agent workflow
- **LangChain**: Chain abstraction for AI reasoning
- **Groq API + LLaMA 3**: Fast LLM responses
- **Streamlit**: Interactive UI
- **boto3**: AWS SDK for Python

---
