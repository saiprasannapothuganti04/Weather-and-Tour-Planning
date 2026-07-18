from groq import Groq
from duckduckgo_search import DDGS
import requests, gradio as gr

client = Groq(api_key="Gemini_API")

MODEL = "llama-3.3-70b-versatile"
def weather(city):

    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name":city,"count":1}
    ).json()

    if "results" not in geo:
        return "City not found"

    p = geo["results"][0]

    data = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude":p["latitude"],
            "longitude":p["longitude"],
            "current":"temperature_2m"
        }
    ).json()

    return f"{city} Temperature : {data['current']['temperature_2m']}°C"
def search(query):

    with DDGS() as d:

        r = list(d.text(query,max_results=3))

    return "\n".join(i["title"] for i in r)
def agent(question):

    decision = client.chat.completions.create(

        model=MODEL,

        messages=[

            {
                "role":"system",
                "content":
                """
                Reply with only one word:

                weather
                search
                both
                none
                """
            },

            {
                "role":"user",
                "content":question
            }

        ]

    ).choices[0].message.content.lower()

    info = ""

    if "weather" in decision or "both" in decision:

        city = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role":"user",
                    "content":f"Extract only the city name from: {question}"
                }
            ]

        ).choices[0].message.content.strip()

        info += weather(city) + "\n\n"

    if "search" in decision or "both" in decision:

        info += search(question)

    answer = client.chat.completions.create(

        model=MODEL,

        messages=[

            {
                "role":"system",
                "content":"Answer using the information provided."
            },

            {
                "role":"user",
                "content":f"Question:\n{question}\n\nInformation:\n{info}"
            }

        ]

    )

    return answer.choices[0].message.content
print(agent("Should I carry an umbrella for Goa and suggest places to visit?"))
gr.ChatInterface(
    fn=lambda x, h: agent(x),
    title="Weather + Trip Planner"
).launch(
    share=True,
    debug=False,
)
