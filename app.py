from flask import Flask, jsonify, request
from flask_cors import CORS
from Agents.GNews import get_news_from_GNews
from Agents.NewsApi import get_news_from_NewsApi
from Agents.Summarizer_agent import get_summarized
from Agents.Rti_Scout_agent import running_rti_document_audit  # Injected the RTI agent
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Maintained existing CORS origin mapping
CORS(app, origins=["http://localhost:5173"])

def simple_sentence_split(text):
    return text.split(".")

def fact_coverage(summary, articles):
    summary_sentences = simple_sentence_split(summary)
    covered = 0
    for sentence in summary_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        found = False
        for article in articles:
            if isinstance(article, dict):
                text = (article.get("title", "") + " " + article.get("description", "")).lower()
            else:
                text = str(article).lower()
            if sentence.lower()[:40] in text:
                found = True
                break
        if found:
            covered += 1
    total_sentences = len([s for s in summary_sentences if s.strip()])
    return covered / total_sentences if total_sentences else 0

def agreement_score(articles):
    word_freq = {}
    for article in articles:
        if isinstance(article, dict):
            text = (article.get("title", "") + " " + article.get("description", "")).lower()
        else:
            text = str(article).lower()
        for word in text.split():
            if len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
    if not word_freq:
        return 0
    common_words = [k for k, v in word_freq.items() if v > 2]
    return len(common_words) / len(word_freq)

def reliability_score(summary, articles):
    fc = fact_coverage(summary, articles)
    ag = agreement_score(articles)
    print("Fact Coverage:", fc)
    print("Agreement Score:", ag)
    score = (0.6 * fc + 0.4 * ag) * 100
    return round(score, 2), fc, ag

def remove_duplicates(news):
    seen = set()
    unique = []
    for article in news:
        title = article.get("title")
        if title not in seen:
            seen.add(title)
            unique.append(article)
    return unique

# Fixed hardcoded groq string to utilize local environment parameters securely
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_search_query(topic):
    prompt = f"""
You are an expert news search assistant.

Convert the given user topic into an optimized news search query for news APIs.

Rules:
- Include important keywords and synonyms
- Expand abbreviations (e.g., USA → United States OR US)
- Add related terms (e.g., war → conflict, military, tensions, attack)
- Keep it concise but information-rich
- Format using OR between similar terms
- Do NOT add explanations, only return the query

Example:
Input: Iran vs USA war
Output: Iran (United States OR US OR America) (war OR conflict OR military OR tensions OR attack)

Now generate for:

Input: {topic}
Output:
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    query = response.choices[0].message.content.strip()
    return query

@app.route('/news', methods=['POST'])
def get_combined_news():
    data = request.json
    if not data or "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400
    topic = data.get("topic").strip()
    if topic == "":
        return jsonify({"error": "Topic cannot be empty"}), 400
    try:
        query = generate_search_query(topic)
        print("Generated Query:", query)
        
        # Pull standard pipeline data feeds
        news1 = get_news_from_GNews(query)
        news2 = get_news_from_NewsApi(query)
        combined_news = remove_duplicates(news1 + news2)
        sources_audited = len(combined_news)
        
        # New Feature: Execute the RTI Section 4 Document Discovery layer
        rti_audit_trail = running_rti_document_audit(topic)
        
        return jsonify({
            "Sources_Audited": sources_audited,
            "articles": combined_news,
            "Rti_Proactive_Audit": rti_audit_trail # Clean, non-destructive payload addition
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/summarized', methods=['POST'])
def get_summarized_news():
    try:
        data = request.json
        articles = data.get("articles")
        if not articles:
            return jsonify({"error": "No articles provided"}), 400
        summarized_news = get_summarized(articles)
        reliability, fc, ag = reliability_score(summarized_news, articles)
        return jsonify({
            "summary": summarized_news,
            "metrics": {
                "fact_coverage": round(fc * 100, 2),
                "agreement_score": round(ag * 100, 2),
                "reliability_score": reliability
            }
        })
    except Exception as e:
        import traceback
        print("ERROR OCCURRED:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
