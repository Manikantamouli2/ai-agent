
import requests
from django.shortcuts import render
from django.conf import settings


def home(request):
    result = None
    if request.method == "POST":
        company = request.POST.get("company")
        role = request.POST.get("role")
        
        query = f"{company} company overview; {role} role requirements"
        
        
        
        tavily= {
            "api_key": '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',
            "query": query,
            "search_depth": "basic",
            "max_results": 5
        }
        tavily_url = "https://api.tavily.com/search"
        tavily_res = requests.post(tavily_url, json=tavily)

        if tavily_res.status_code != 200:
            return render(request, "jobmini/home.html", {"result": "Error fetching data from Tavily API."})

        tavily_data = tavily_res.json()
        raw_text = "\n\n".join(f"{item.get('title', '')}\n{item.get('content', '')}" for item in tavily_data.get("results", []))

        if not raw_text.strip():
            return render(request, "jobmini/home.html", {"result": "No relevant data found."})

        
        gemini_api_key = 'AIzaSyASoHapHCpAmgpu43kPFc9KspmcKRDw8Pg'
        gemini_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={gemini_api_key}"
        )

        prompt = (
            "Summarize the following data into two sections:\n"
            "1. Company Overview (size, domain, latest news)\n"
            "2. Role-specific Requirements (skills, experience, salary range)\n\n"
            f"Data:\n{raw_text}"
        )

        gemini_payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        gemini_resp = requests.post(gemini_url, json=gemini_payload)

        if gemini_resp.status_code != 200:
            return render(request, "jobmini/home.html", {"result": "Error summarizing data with Gemini."})

        try:
            summary = gemini_resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            summary = "Error parsing Gemini API response."

        result = summary

    return render(request, "jobmini/home.html", {"result": result})
