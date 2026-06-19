import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # ከቴሌግራም ዌብሁክ የሚመጣን ፎቶ ወይም ቪዲዮ ቼክ ማድረግ
            if "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                message_id = message["message_id"]

                # ፎቶ (photo) ወይም ቪዲዮ (video) መኖሩን ማረጋገጥ
                is_media = "photo" in message or "video" in message

                if is_media:
                    # ፋይሉን በቀጥታ ወደ ማከማቻ ቻናሉ Forward ማድረግ
                    forward_url = f"https://api.telegram.org/bot{BOT_TOKEN}/forwardMessage"
                    payload = {
                        "chat_id": TELEGRAM_CHANNEL_ID,
                        "from_chat_id": chat_id,
                        "message_id": message_id
                    }
                    
                    response = requests.post(forward_url, json=payload)
                    if response.status_code == 200:
                        # ስኬታማ ከሆነ ለተጠቃሚው ማረጋገጫ መላክ
                        reply_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        reply_payload = {
                            "chat_id": chat_id,
                            "text": "✅ SUCCESS: ፋይሉ በሰላም ደመና (Cloud) ላይ አርፏል። ስልክህ ላይ ያለውን ማጥፋት ትችላለህ!",
                            "reply_to_message_id": message_id
                        }
                        requests.post(reply_url, json=reply_payload)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
