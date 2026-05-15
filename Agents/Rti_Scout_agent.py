import requests
from googlesearch import search
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def running_rti_document_audit(topic):
    # Check if topic relates to infrastructure, tenders, contracts, or public assets
    audit_keywords = ["bridge", "road", "highway", "contract", "tender", "construction", "scam", "allocation", "budget", "project"]
    if not any(word in topic.lower() for word in audit_keywords):
        return "No infrastructure or public project keywords identified. RTI Section 4 Document Scout stood down."

    print(f"🔍 RTI Document Scout triggered for public asset topic: {topic}")
    
    # Advanced search engine dork matching legal Section 4 manual frameworks and procurement files
    dork_query = f'site:*.gov.in "{topic}" (tender OR contract OR "bid award" OR "Manual 11" OR "proactive disclosure")'
    
    discovered_docs = []
    try:
        # Search the web for public government documents matching criteria
        for url in search(dork_query, num_results=4):
            if url.endswith(".pdf") or "tender" in url or "rti" in url:
                discovered_docs.append(url)
    except Exception as e:
        print("Google Search Scraper Exception:", e)

    if not discovered_docs:
        return "RTI Status: No proactively disclosed Section 4 baseline manuals or active tender sheets located on official public directories."

    # Construct verification context for Groq analysis
    context_links = "\n".join([f"- {link}" for link in discovered_docs])
    
    prompt = f"""
    You are an expert Government Audit Assistant specialized in RTI Section 4(1)(b) Proactive Disclosures.
    A user is searching for news regarding: "{topic}".
    Our data scrapers found the following official public government links relating to this topic:
    {context_links}

    Based on these source URLs, construct a brief 3-4 sentence verification outline for a student project report:
    1. Confirm that official records exist on state/national public directories.
    2. Extract or infer which specific department/portal (e.g., CPPP, eprocure, State Portals) hosts the data tracking records.
    3. State how a citizen can use Manual 11 (Budget Allocations) or Manual 15 to find contract values, winning companies, and implementation timelines.
    
    Be objective and professional. Provide the direct links at the end under 'Verified Reference Links'.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"RTI Auditor Exception: Document references found but summary failed to execute. Source URLs discovered:\n{context_links}"
