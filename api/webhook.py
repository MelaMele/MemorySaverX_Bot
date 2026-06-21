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
            
            # 1. መጀመሪያ ፋይሉን ወደ ቴሌግራም መላክ (Vercel ሳይዘጋ እንዲጨርስ)
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            files = {'document': ('camera_file.jpg', post_data)}
            data = {'chat_id': TELEGRAM_CHANNEL_ID}
            
            try:
                # ቴሌግራም ፋይሉን ተቀብሎ እስኪጨርስ ሰርቨሩ ይጠብቃል
                tg_response = requests.post(url, files=files, data=data, timeout=45)
                
                if tg_response.status_code == 200:
                    # 2. ቴሌግራም ላይ በሰላም መድረሱን ካረጋገጥን በኋላ ብቻ ለስልኩ 200 መመለስ
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "message": "File sent to Telegram and cleared"}).encode('utf-8'))
                else:
                    # ቴሌግራም እምቢ ካለ ለስልኩ Error እንመልሳለን (ስልክህ ላይ እንዳይጠፋ)
                    self.send_response(tg_response.status_code)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "reason": "Telegram rejected"}).encode('utf-8'))
            except Exception as e:
                # የሰርቨር ወይም የቴሌግራም ኔትወርክ ከተቋረጠ ስልኩ ላይ እንዳይጠፋ 500 መመለስ
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "reason": str(e)}).encode('utf-8'))
            return
                
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
