import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
# የቻናል IDህን በቀጥታ እዚህም አስገብቼዋለሁ፡ -1004388764838
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "-1004388764838")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        status_code = 200
        response_body = {"status": "ok"}

        # 1. መረጃው ከስልኩ በቀጥታ የመጣ ፋይል (multipart) ከሆነ
        if 'multipart/form-data' in content_type:
            try:
                if len(post_data) > 0:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                    files = {'document': ('camera_file.jpg', post_data)}
                    data = {'chat_id': TELEGRAM_CHANNEL_ID}
                    requests.post(url, files=files, data=data, timeout=30)
                    response_body = {"status": "success"}
            except Exception as e:
                status_code = 500
                response_body = {"status": "error", "reason": str(e)}

        # 2. መረጃው ከቴሌግራም ዌብሁክ (JSON) የመጣ መደበኛ መልእክት ከሆነ
        else:
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # መልእክት (Message) መኖሩን ቼክ ማድረግ
                if "message" in data:
                    message = data["message"]
                    
                    # የጽሑፍ መልእክት ከሆነ ወደ ቻናሉ ፎርዋርድ ማድረግ ወይም መላክ
                    if "text" in message:
                        text_to_send = message["text"]
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        payload = {
                            "chat_id": TELEGRAM_CHANNEL_ID,
                            "text": f"የመጣ መልእክት፦ {text_to_send}"
                        }
                        requests.post(url, json=payload, timeout=30)
                        
                    # ፎቶ ከሆነ ወደ ቻናሉ ማስተላለፍ
                    elif "photo" in message:
                        # ከፍተኛ ጥራት ያለውን ፎቶ መምረጥ
                        photo_id = message["photo"][-1]["file_id"]
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                        payload = {
                            "chat_id": TELEGRAM_CHANNEL_ID,
                            "photo": photo_id
                        }
                        requests.post(url, json=payload, timeout=30)
                        
            except Exception as e:
                # ዌብሁኩ ሁልጊዜ 200 መመለስ አለበት እንዳይደጋገም
                response_body = {"status": "json_parse_error", "reason": str(e)}

        # ምላሽ መጻፍ
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
