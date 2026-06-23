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

        # 1. መረጃው ከስልኩ የመጣ ንጹህ የፋይል ዳታ ወይም መደበኛ ማስተላለፊያ ከሆነ
        if 'multipart/form-data' in content_type or (content_length > 0 and not content_type.startswith('application/json')):
            try:
                # የ multipart boundary ማጽጃ (አስፈላጊ ከሆነ)
                # ለቀላሉ በቀጥታ ሙሉውን ዳታ እንደ ፎቶ እንልከዋለን
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                files = {'photo': ('camera_file.jpg', post_data)}
                data = {'chat_id': TELEGRAM_CHANNEL_ID, 'caption': '🔄 Backup Saved'}
                
                res = requests.post(url, files=files, data=data, timeout=30)
                res_json = res.json()
                
                if not res_json.get("ok"):
                    # የቴሌግራም ስህተት ካለ በቪፒኤን/ሎግ ላይ እንዲታይ
                    print(f"Telegram Error: {res_json}")
                    status_code = 400
                    response_body = {"status": "telegram_rejected", "details": res_json}
                else:
                    response_body = {"status": "success"}
                    
            except Exception as e:
                status_code = -100 # Internal Error
                response_body = {"status": "error", "reason": str(e)}

        # 2. መረጃው ከቴሌግራም ዌብሁክ (JSON) የመጣ ከሆነ
        else:
            try:
                if post_data:
                    data = json.loads(post_data.decode('utf-8'))
                    
                    if "message" in data:
                        message = data["message"]
                        
                        # የጽሑፍ መልእክት ፍተሻ
                        if "text" in message:
                            text_to_send = message["text"]
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                            payload = {
                                "chat_id": TELEGRAM_CHANNEL_ID,
                                "text": f"📩 የመጣ መልእክት፦ {text_to_send}"
                            }
                            requests.post(url, json=payload, timeout=30)
                            
                        # የፎቶ መልእክት ፍተሻ
                        elif "photo" in message:
                            photo_id = message["photo"][-1]["file_id"]
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                            payload = {
                                "chat_id": TELEGRAM_CHANNEL_ID,
                                "photo": photo_id
                            }
                            requests.post(url, json=payload, timeout=30)
            except Exception as e:
                print(f"JSON Error: {str(e)}")
                response_body = {"status": "json_parse_error", "reason": str(e)}

        # ምላሽ መጻፍ
        self.send_response(200 if status_code == 200 else 200) # ቴሌግራም እንዳይደግመው ሁልጊዜ 200 እንመልስ
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
