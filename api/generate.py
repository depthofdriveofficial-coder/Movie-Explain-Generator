from http.server import BaseHTTPRequestHandler
import http.client, json, os

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))

            movie = body.get('movie', '')
            srt_content = body.get('srt', '')
            language = body.get('language', 'English')
            platform = body.get('platform', 'YouTube Shorts')
            style = body.get('style', 'Thriller')
            duration = body.get('duration', '60 Seconds')

            lang_instruction = {
                'Urdu': 'STRICTLY write everything in Urdu script (اردو). Do NOT use Roman Urdu or English words except proper nouns.',
                'Hindi': 'STRICTLY write everything in Hindi (हिंदी). Do NOT use Roman Hindi or English words except proper nouns.',
                'Hinglish': 'Write in Hinglish — mix of Hindi/Urdu words written in Roman script with some English.',
                'English': 'STRICTLY write everything in English only. Do NOT use any Urdu, Hindi or Roman Urdu words at all.',
                'Arabic': 'STRICTLY write everything in Arabic (العربية). Do NOT use any other language except proper nouns.',
            }.get(language, 'STRICTLY write everything in English only.')

            prompt = f"""You are a world-class viral movie storytelling scriptwriter. Your scripts have generated millions of views on YouTube Shorts, TikTok and Instagram Reels.

MOVIE: {movie}
PLATFORM: {platform}
STYLE: {style}
DURATION: {duration}
LANGUAGE RULE: {lang_instruction}

SRT SUBTITLE FILE:
{srt_content[:8000]}

CRITICAL RULES:
1. {lang_instruction}
2. Write like a HUMAN STORYTELLER — not a reviewer or analyst
3. Create EMOTION — make viewers feel fear, excitement, shock, curiosity
4. Every 2-3 lines must have a curiosity hook to keep watching
5. Use dramatic pacing — [Pause], [Whisper], [Shock], [Suspense] markers
6. Script must match the {duration} duration exactly

BAD EXAMPLE (never do this):
"The protagonist faces many challenges in this film."

GOOD EXAMPLE (always like this):
"Uske haath kaanp rahe the... [Pause] Aur phir usne woh darwaza khola jise khol kar uski zindagi hamesha ke liye badal gayi... [Shock]"

OUTPUT FORMAT:

## 🎬 VIRAL CONCEPT
[Name + Why it will explode on {platform}]

## ⚡ HOOK (First 3 seconds)
[One line that stops the scroll — most important part]

## 📝 FULL VOICEOVER SCRIPT
[Complete script in {language} — storyteller style with emotion markers]

## 🎞️ MICRO-CLIP EDITING PLAN
For each section provide:
⏱ Timestamp: [from SRT]
🎬 Scene: [what to show]
🎤 Lines: [voiceover for this section]
✂️ Edit: [cut/zoom/transition tip]

## 📱 SEO PACKAGE (Always in English)
Title: [click-bait but accurate title]
Description: [150 word SEO description]
Hashtags: [20 relevant hashtags]
Hook Text: [on-screen text overlay for first 3 seconds]
CTA: [end screen call to action]"""

            api_key = os.environ.get("GROQ_API_KEY", "")

            payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an expert viral content creator. You MUST write the script ONLY in {language}. {lang_instruction} Never mix languages unless writing Hinglish."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.8
            }).encode()

            conn = http.client.HTTPSConnection("api.groq.com")
            conn.request("POST", "/openai/v1/chat/completions", payload, {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })

            res = conn.getresponse()
            data = json.loads(res.read().decode())
            reply = data["choices"][0]["message"]["content"]

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"script": reply}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
