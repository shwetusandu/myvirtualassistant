from fastapi import FastAPI
from fastapi_pagination import response
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from typer import prompt
import config as ModelConfig
import json
import uvicorn
import os

load_dotenv()

port = int(os.environ.get("PORT", 8000))

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Req(BaseModel):
    user_id: str
    message: str

@app.post("/assistant")
def assistant(req: Req):

    prompt = f"""
You are MyVirtualAssistant AI Processor.

Analyze the user message and return ONLY valid JSON.

Do not add explanation.
Do not add markdown.
Do not add ```json.
Return raw JSON only.

JSON Format:

{{
  "user_id": "",
  "message": "",
  "request_type": "",
  "url_category": "",
  "tool_to_call": "",
  "action": "",
  "result": ""
}}

Rules:

1. request_type must be one of:
URL
Rewrite
Task
Note
Idea
Meaning
General

2. If message contains URL:
request_type = URL

If message starts with rewrite or rephrase:
request_type = Rewrite

If message starts with task:
request_type = Task

If message starts with note:
request_type = Note

If message starts with idea:
request_type = Idea

If message is a single word:
request_type = Meaning

Otherwise:
request_type = General

3. url_category only for URL requests:
Jewellery
Clothing
Accessories
Home Decor
AI Materials
General Materials
Instagram
Other

If not URL, keep url_category empty.

4. tool_to_call values:
url_tool
rewrite_tool
task_tool
note_tool
idea_tool
meaning_tool
general_tool

5. action = what should happen next in short text.

Examples:
Bookmark URL
Rewrite sentence
Save task
Save note
Generate project idea
Give meaning
General reply

6. result rules:

If URL:
Return short summary within 250 characters.

If Rewrite:
Return rewritten text.

If Task:
Return task name extracted.

If Note:
Return note text.

If Idea:
Return short expanded idea.

If Meaning:
Return word meaning.

If General:
Return short helpful reply.

7. Always preserve original user message in "message"

Now process this user input:

User ID: {req.user_id}
Message: {req.message}
"""

    response = client.chat.completions.create(
        model=ModelConfig.MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    print(f"Prompt:\n{prompt}\n")
    print(f"Response:\n{response.choices[0].message.content}\n")

    return json.loads(response.choices[0].message.content)
