import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8614580780:AAEN5iQifNzbf5fw6iOsdVN6fTweMK86TnU")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "-1004388764838")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        status_code = 200
        response_body = {"status": "ok"}

        if 'multipart/form-data' in content_type:
            try:
                # ከስልክ የሚመጣውን ፎቶ ወደ ቴሌግራም ማስተላለፍ
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                headers = {'Content-Type': content_type}
                
                res = requests.post(url, data=post_data, headers=headers, params={'chat_id': TELEGRAM_CHANNEL_ID}, timeout=30)
                res_json = res.json()
                
                if res.status_code == 200 and res_json.get("ok"):
                    response_body = {"status": "success"}
                    status_code = 200
                else:
                    # ቴሌግራም እምቢ ካለ እውነተኛውን ስህተት ለስልኩ መመለስ
                    status_code = 500
                    response_body = {"status": "telegram_rejected", "details": res_json}
            except Exception as e:
                status_code = 500
                response_body = {"status": "error", "reason": str(e)}
        else:
            # የቴሌግራም ዌብሁክ (JSON) አያያዝ
            try:
                if post_data:
                    data = json.loads(post_data.decode('utf-8'))
                    if "message" in data:
                        message = data["message"]
                        if "text" in message:
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHANNEL_ID, "text": f"📩 {message['text']}"}, timeout=30)
                        elif "photo" in message:
                            photo_id = message["photo"][-1]["file_id"]
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", json={"chat_id": TELEGRAM_CHANNEL_ID, "photo": photo_id}, timeout=30)
            except Exception as e:
                response_body = {"status": "json_parse_error", "reason": str(e)}

        # ምላሹን በትክክለኛው የ Status Code መጻፍ
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
