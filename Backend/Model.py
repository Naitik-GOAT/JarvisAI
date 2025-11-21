import os
import sys
from dotenv import dotenv_values
import cohere
from rich import print

# ------------------------------------------------------------------
# 1. Load the .env that sits ONE level above this file (JarvisAI/.env)
# ------------------------------------------------------------------
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
env_vars = dotenv_values(env_path)

# ------------------------------------------------------------------
# 2. Grab the API key (env var name must match what’s in .env)
# ------------------------------------------------------------------
CohereAPIKey = env_vars.get("CohereAPIKey")  # <-- make sure it's spelled the same

if not CohereAPIKey:
    sys.exit("[red]❌ CohereAPIKey not found in .env[/red]")

print("[green]DEBUG – key loaded:[/green]", CohereAPIKey[:6] + "...")

# ------------------------------------------------------------------
# 3. Create the Cohere client – using correct argument (not 'token')
# ------------------------------------------------------------------
co = cohere.Client(CohereAPIKey)

# ------------------------------------------------------------------
# 4. Define function keywords and preamble
# ------------------------------------------------------------------
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

preamble = """
You are an intelligent assistant designed to categorize user inputs into specific functional tasks. Always identify and label each part of the user's message according to one of the following function categories:

- 'exit'
- 'general' (for casual conversation or questions without a clear command)
- 'realtime' (time-sensitive queries, like the current date or time)
- 'open' (to open applications or websites)
- 'close' (to close applications or tabs)
- 'play' (for playing media such as songs or videos)
- 'generate image' (requests to create or visualize images)
- 'system' (system-level actions like shutting down, restarting)
- 'content' (content generation or writing tasks)
- 'google search' (search queries meant for Google)
- 'youtube search' (search queries meant for YouTube)
- 'reminder' (any request to set a reminder or alert)

Respond only with a concise list of tasks, each starting with one of the above function keywords, and preserve the order of actions. If a message includes multiple actions, separate them into individual task lines.

Example:
User: "open chrome and play music"
Response: "open chrome, play music"

Avoid explanations, markdown, or extra commentary. Just return the labeled commands as a plain list.
"""

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

# ------------------------------------------------------------------
# 5. Core function for task categorization
# ------------------------------------------------------------------
def FirstLayerDMM(prompt: str = 'test'):
    messages.append({"role": "user", "content": f"{prompt}"})

    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation="OFF",
        connectors=[],
        preamble=preamble
    )

    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    response = response.replace("\n", " ")
    response = response.split(".")

    response = [i.strip() for i in response]

    temp = []
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)

    response = temp

    if "query" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return response

# ------------------------------------------------------------------
# 6. Interactive loop (main entry)
# ------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))
