# Autonomous Multi-Agent Research & Decision System

Starter milestone for Windows + VS Code using a local open-source LLM through Ollama.

## 1. Prerequisites
- Python 3.11 recommended
- Ollama for Windows: https://ollama.com/download/windows

## 2. Download the model
Open PowerShell:

```powershell
ollama pull llama3.2
ollama run llama3.2
```

Type `/bye` to exit the model chat.

Check the local API:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

## 3. Set up this project
Extract the ZIP, open the extracted `autonomous-research-system` folder in VS Code, then run in its terminal:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If Python 3.11 is not installed, install it first. You can also use another installed Python version compatible with the packages by replacing `py -3.11`.

## 4. Start the API
From the folder containing `main.py`:

```powershell
uvicorn main:app --reload
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## 5. Test `/research`
In `/docs`, expand `POST /research`, click **Try it out**, and submit:

```json
{
  "question": "Compare RAG and fine-tuning for a research assistant."
}
```

The response includes the model answer and latency.

## Current scope
This is the first working API milestone. It connects to local Llama and exposes health and research endpoints. Web search, the four specialized agents, hybrid RAG, reranking, persistent memory, citations, evaluation, approval flow, and observability are planned next.
