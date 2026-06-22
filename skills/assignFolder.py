from ollama import chat
from skills.createFF import getfolderList

def askFolder(query_text: str):
    
    prompt = f"""The following is a list of available folders:
    {', '.join(getfolderList())}
    Please select a folder that best fits the user's query: {query_text}
    Answer ONLY with the name of the folder."""

    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return(response.message.content)