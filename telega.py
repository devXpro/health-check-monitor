import json
import os
import requests
import time
import db

import load_env

load_env.load_env()


class TelBot:
    def __init__(self):
        self.process = None
        self.update_id = 0
        self.password = os.getenv('BOT_PASSWORD')
        api_url = "https://api.telegram.org/bot"
        token = os.getenv('TELEGRAM_TOKEN')
        self.base_url = api_url + token
        self.db = db.DB()

    def loop(self):
        while True:
            for massage in self.get_new_messages():
                self.handle_message(massage)
            time.sleep(1)

    def check_out(self):
        for name, url, groups, online in self.db.get_all_urls():
            success = True
            try:
                if requests.get(url).status_code not in [200, 301, 302]:
                    success = False
            except Exception:
                success = False
            if online == 1 and not success:
                online = 0
            elif online == 0 and success:
                online = 1
            else:
                return
            self.db.update_url_status(name, online)
            for chat_id in self.db.find_chats_by_groups(json.loads(groups)):
                message = 'is not responding!' if online == 0 else "was repaired successfully"
                self.send_message(chat_id, f'ALERT! Project "{name}"' + message)

    def login(self, chat, text):
        chat_id = chat['id']
        user = self.db.find_user(chat_id)
        if not user:
            group = self.db.get_group_by_password(text)
            if group:
                self.db.add_user(chat_id, group)
                return True
            else:
                self.send_message(chat_id, 'Please type password')
                return False
        return True

    def handle_message(self, message):
        chat_id = message['chat']['id']
        if 'text' not in message:
            return
        text = message['text']
        if not self.login(message['chat'], text):
            return
        if text == '/logout':
            self.db.delete_user(chat_id)
            self.send_message(chat_id, "Log out successfully.")
            return
        self.send_subscribed_urls(chat_id)

    def send_subscribed_urls(self, chat_id):
        urls = self.db.get_urls_by_chat_id(chat_id)
        self.send_message(chat_id, "Subscribed projects:")
        for name, _, _, online in urls:
            self.send_message(chat_id, f'- {name} ({"online" if online == 1 else "offline"})')

    def get_new_messages(self):
        offset_string = '?offset=' + str(self.update_id + 1) if self.update_id != 0 else ''
        try:
            response = requests.get(self.base_url + '/getUpdates' + offset_string).json()
        except Exception:
            print("Telegram API is not available!")
            return []
        messages = []
        for message in response['result']:
            self.update_id = message['update_id']
            if 'callback_query' in message:
                message['callback_query']['message']['text'] = message['callback_query']['data']
                messages.append(message['callback_query']['message'])
            elif 'edited_message' in message:
                continue
            else:
                messages.append(message['message'])
        return messages

    def send_message(self, chat_id, text):
        try:
            if "[img]" not in text:
                requests.post(self.base_url + '/sendMessage' + '?chat_id=' + str(chat_id) + '&text=' + text)
            else:
                data = {"chat_id": chat_id}
                with open(text.replace('[img]', ''), "rb") as image_file:
                    requests.post(self.base_url + '/sendPhoto', data=data, files={"photo": image_file})
        except Exception:
            print('Connection with telegram was lost')

    def send_html_message(self, html, chat_id):
        data = {"chat_id": chat_id,
                "parse_mode": 'html',
                "text": html}

        requests.post(url=self.base_url + '/sendMessage', data=data)
