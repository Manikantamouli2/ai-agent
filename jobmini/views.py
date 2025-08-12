
import requests
import os
from django.shortcuts import render
def home(request):
    result = None
    if request.method == "POST":
        company = request.POST.get("company")
        role = request.POST.get("role")
        print(company)
        print(role)
        query = f"{company} company overview; {role} role requirements"

        tavily_payload = {
            "api_key": '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',
            "query": query,
            "search_depth": "basic",
            "max_results": 5
        }
        tavily_url = "https://api.tavily.com/search"
        tavily_resp = requests.post(tavily_url, json=tavily_payload)

        if tavily_resp.status_code != 200:
            result = "Error fetching data from Tavily API."
            return render(request, "jobmini/home.html", {"result": result})

        tavily_data = tavily_resp.json()
        print(tavily_data)
        raw_text = ""
        for item in tavily_data.get("results", []):
            title = item.get("title", "")
            content = item.get("content", "")
            raw_text += f"{title}\n{content}\n\n"
            print(raw_text)
        if not raw_text.strip():
            result = "No relevant data found."
            return render(request, "jobmini/home.html", {"result": result})
         # Step 2: Gemini API summarization
        gemini_api_key = "AIzaSyASoHapHCpAmgpu43kPFc9KspmcKRDw8Pg"  # <-- Replace with your actual key
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
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        gemini_resp = requests.post(gemini_url, json=gemini_payload)
        print(gemini_resp)

        if gemini_resp.status_code != 200:
            print("Gemini API error:", gemini_resp.status_code, gemini_resp.text)
            result = "Error summarizing data with Gemini."
            return render(request, "jobmini/home.html", {"result": result})

        gemini_data = gemini_resp.json()
        print("Gemini Response:", gemini_data)

        try:
            summary = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            summary = "Error parsing Gemini API response."

        result = summary

    return render(request, "jobmini/home.html", {"result": result})
        
        


    return render(request, "jobmini/home.html", {"result": result})

    


       
            

