## OpenAI Agent (Python) with Google Search Tool

This project demonstrates a minimal "agent" powered by the experimental OpenAI Agents SDK for Python. The agent is a helpful assistant that performs a simple Google search when prompted before answering.

### Prerequisites

- Python 3.9+
- An OpenAI API key with access to the latest APIs (set `OPENAI_API_KEY`).

### Setup

1. Create and activate a virtual environment (Windows PowerShell shown):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set your OpenAI API key in the environment:

```powershell
$Env:OPENAI_API_KEY = "sk-..."
```

### Run (Agents SDK example)

```powershell
python .\assistant_agent.py
```

Type a question that needs a lookup, e.g.: "Search for the latest AI news on GPT models". The agent will call the `google_search` tool first, then compose a concise reply.

### Notes

- The included search tool uses basic HTML scraping from Google, which can be brittle and may violate Google's Terms of Service. For production, use an official API such as Google Custom Search JSON API or SerpAPI, and adapt the `google_search` tool accordingly.
- The OpenAI Agents SDK used here is experimental and its API may change. Refer to the latest docs for updates.

### Alternative: Official OpenAI Python SDK with tool-calling

If you encounter issues with the experimental Agents SDK on your platform, use the alternative script based on the official OpenAI Python SDK:

```powershell
python .\assistant_toolcalling.py
```

It exposes the same capability: when you ask to look something up, it first performs a Google search, then summarizes the findings.

This variant also uses Pydantic models (`SearchResult`, `SearchResponse`) to structure tool output.

### References

- OpenAI Agents SDK (Python): `https://openai.github.io/openai-agents-python/`
- OpenAI Platform: `https://platform.openai.com/`


