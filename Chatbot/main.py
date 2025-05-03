from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from openai import OpenAI

# Initialize FastAPI
app = FastAPI()

# Template directory
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI client with your API key
client = OpenAI(api_key="YOUR_API_KEY")

# Error logging for debugging
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"🔥 Error occurred: {exc}")
    return PlainTextResponse(str(exc), status_code=500)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"⚠️ HTTP error occurred: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    print("🚀 GET / route called")
    return templates.TemplateResponse("home.html", {"request": request, "chat": []})

@app.post("/", response_class=HTMLResponse)
async def post_chat(request: Request, user_input: str = Form(...)):
    print(f"📨 User input received: {user_input}")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4o-mini" if that's valid
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        bot_reply = response.choices[0].message.content
        print(f"🤖 Bot reply: {bot_reply}")
    except Exception as e:
        bot_reply = f"Error: {str(e)}"
        print(f"❌ Error while calling OpenAI API: {e}")

    return templates.TemplateResponse("home.html", {
        "request": request,
        "chat": [{"user": user_input, "bot": bot_reply}]
    })
