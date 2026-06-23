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

        # 1. መረጃው ከስልክህ በ requests.post(files={'photo': ...}) የመጣ ከሆነ
        if 'multipart/form-data' in content_type:
            try:
                # ከስልክ የሚመጣውን ፎቶ በቀጥታ ፎርዋርድ ለማድረግ
                # ቀላሉ መንገድ ሙሉውን post_data መላክ ሳይሆን በ multipart ፎርማት ማስተላለፍ ነው
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                
                # መልእክቱን ወደ ቴሌግራም ፓስ ማድረግ (Header እና የሴክሽን ዳታውን ጨምሮ)
                headers = {'Content-Type': content_type}
                res = requests.post(url, data=post_data, headers=headers, params={'chat_id': TELEGRAM_CHANNEL_ID}, timeout=30)
                
                if res.status_code == 200:
                    response_body = {"status": "success"}
                else:
                    response_body = {"status": "telegram_error", "details": res.json()}
            except Exception as e:
                response_body = {"status": "error", "reason": str(e)}

        # 2. መረጃው ከቴሌግራም ዌብሁክ (JSON) የመጣ መደበኛ መልእክት ከሆነ
        else:
            try:
                if post_data:
                    data = json.loads(post_data.decode('utf-8'))
                    if "message" in data:
                        message = data["message"]
                        
                        # የጽሑፍ ፍተሻ
                        if "text" in message:
                            text_to_send = message["text"]
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                            requests.post(url, json={"chat_id": TELEGRAM_CHANNEL_ID, "text": f"📩 {text_to_send}"}, timeout=30)
                            
                        # የፎቶ ፍተሻ (ከቴሌግራም ወደ ቻናል)
                        elif "photo" in message:
                            photo_id = message["photo"][-1]["file_id"]
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                            requests.post(url, json={"chat_id": TELEGRAM_CHANNEL_ID, "photo": photo_id}, timeout=30)
            except Exception as e:
                response_body = {"status": "json_parse_error", "reason": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
