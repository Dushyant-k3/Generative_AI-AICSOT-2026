import os
import json
import requests
import urllib.request

import xml.etree.ElementTree as ET
from openai import OpenAI
from dotenv import load_dotenv

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, RichLog

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

MODEL = "openrouter/free"
MAX_HISTORY_TURNS = 20
MAX_ITERATIONS = 8


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the Google web index using Serper API. Use this to find current events, facts, or URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Fetches and extracts the text content from a given URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full HTTP URL of the webpage to read."}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "discover_papers",
            "description": "Searches for academic scientific papers based on a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The topic to search for, e.g., 'quantum computing'"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_paper_content",
            "description": "Reads the abstract and details of a specific scientific paper using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "The ID of the paper to read."}
                },
                "required": ["paper_id"],
            },
        },
    }
]

# 2. Tool Implementations 

def search_web(query: str) -> dict:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ.get("SERPER_API_KEY", ""),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def read_page(url: str) -> dict:
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        if text:
            return {"content": text[:4000]} 
        return {"error": "Could not extract text from the page."}
    except Exception as e:
        return {"error": str(e)}

def discover_papers(query: str) -> dict:
    safe_query = query.replace(" ", "+")
    url = f'http://export.arxiv.org/api/query?search_query=all:{safe_query}&start=0&max_results=3'
    try:
        data = urllib.request.urlopen(url).read()
        root = ET.fromstring(data)
        papers = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.replace('\n', ' ')
            papers.append({"id": paper_id, "title": title})
        return {"papers": papers}
    except Exception as e:
        return {"error": str(e)}

def get_paper_content(paper_id: str) -> dict:
    url = f'http://export.arxiv.org/api/query?id_list={paper_id}'
    try:
        data = urllib.request.urlopen(url).read()
        root = ET.fromstring(data)
        entry = root.find('{http://www.w3.org/2005/Atom}entry')
        if entry is not None:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.replace('\n', ' ')
            abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.replace('\n', ' ')
            return {"title": title, "abstract": abstract}
        return {"error": "Paper not found."}
    except Exception as e:
        return {"error": str(e)}

TOOL_REGISTRY = {
    "search_web": search_web,
    "read_page": read_page,
    "discover_papers": discover_papers,
    "get_paper_content": get_paper_content
}

def dispatch(tool_call) -> str:
    name = tool_call.function.name
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse arguments."})
    
    if name not in TOOL_REGISTRY:
        return json.dumps({"error": f"Unknown tool: {name}"})
    
    try:
        result = TOOL_REGISTRY[name](**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def trim_history(messages: list[dict], max_turns: int) -> list[dict]:
    system_prompt = [messages[0]]
    history = messages[1:][-(max_turns*2):]
    return system_prompt + history

# 4. Textual UI & Agent Loop

class ChatApp(App):
    TITLE = "Autonomous Research Agent"
    CSS = """
    Screen { layout: vertical; }
    RichLog { height: 1fr; border: solid $primary; padding: 0 1; }
    Input { dock: bottom; height: 3; }
    """
    BINDINGS = [
        Binding("ctrl+l", "clear_display", "Clear display"),
        Binding("ctrl+k", "clear_history", "Clear history"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.messages: list[dict] = [
            {"role": "system", "content": "You are a helpful Research Assistant. Use your tools to find accurate information."}
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="log", wrap=True, markup=True, highlight=True)
        yield Input(placeholder="Ask me to research something...")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#log", RichLog)
        log.write("[bold green]Research Agent Online.[/bold green] Ctrl+Q to quit.\n")
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text: return
        event.input.clear()
        
        log = self.query_one("#log", RichLog)
        log.write(f"\n[bold cyan][You][/bold cyan] {user_text}")

        self.messages.append({"role": "user", "content": user_text})
        self.messages = trim_history(self.messages, MAX_HISTORY_TURNS)
        self.run_worker(self._get_response(), thread=True)

    async def _get_response(self) -> None:
        log = self.query_one("#log", RichLog)
        try:
            for _ in range(MAX_ITERATIONS):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=self.messages,
                    tools=TOOLS
                )
                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                if finish_reason == "tool_calls":
                    self.messages.append(message)
                    for tool_call in message.tool_calls:
                        self.call_from_thread(log.write, f"[dim italic]...using tool: {tool_call.function.name}[/dim italic]")
                        result_json = dispatch(tool_call)
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_json
                        })
                elif finish_reason == "stop":
                    reply = message.content
                    self.messages.append({'role': "assistant", "content": reply})
                    self.call_from_thread(log.write, f"\n[bold magenta][Agent][/bold magenta] {reply}\n")
                    break
        except Exception as e:
            self.call_from_thread(log.write, f"\n[bold red]Error:[/bold red] {str(e)}\n")

    def action_clear_display(self) -> None:
        self.query_one("#log", RichLog).clear()

    def action_clear_history(self) -> None:
        self.messages = [self.messages[0]]
        log = self.query_one("#log", RichLog)
        log.clear()
        log.write("[bold yellow]Memory wiped. Fresh start.[/bold yellow]\n")

if __name__ == "__main__":
    ChatApp().run()