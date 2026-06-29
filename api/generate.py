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
            language = body.get('language', 'Urdu')
            platform = body.get('platform', 'YouTube Shorts')
            style = body.get('style', 'Thriller')
            duration = body.get('duration', '60 Seconds')

            prompt = f"""You are an Elite Movie Storytelling Agent and Viral Content Creator.

Movie: {movie}
Platform: {platform}
Style/Angle: {style}
Video Duration: {duration}
Script Language: {language}

SRT Subtitle Content:
{srt_content[:8000]}

Your task:
1. Analyze the SRT content deeply
2. Find the BEST viral storytelling angle based on style: {style}
3. Write a complete viral video script in {language}

Output Format:

## 🎬 VIRAL CONCEPT
[Concept name and why it will go viral]

## 🎯 HOOK (First 3 seconds)
[Ultra attention grabbing opening line]

## 📝 FULL SCRIPT
[Complete storytelling script in {language} - human narrator style, NOT review/analysis]
[Add [Pause], [Whisper], [Shock] markers]
[Every few lines add curiosity hooks like "lekin asli twist abhi baqi tha..."]

## 🎞️ MICRO-CLIP PLAN
[For each script section, provide exact timestamp from SRT + scene description]
Format:
**Section 1**
⏱ Timestamp: HH:MM:SS - HH:MM:SS
🎬 Scene: [what happens]
🎤 Voiceover: [script lines]
✨ Effect: [zoom/cut suggestion]

## 📱 SEO PACKAGE (English)
**Title:** [Platform optimized title]
**Description:** [SEO description]
**Hashtags:** [relevant hashtags]
**Hook:** [scroll stopping hook]
**CTA:** [call to action]"""

            api_key = os.environ.get("GROQ_API_KEY", "")

            payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000
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

