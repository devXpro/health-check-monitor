import sqlite3
import json


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(".docker/data/sqlite/database.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                  (chat_id integer, `group` text)
               """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS config
                  (name text, value text, chat_id integer)
               """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `group`
                  (name text, `password` text)
               """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `url`
                  (`name` text, `url` text, `groups` text, online INTEGER default 1, xpath text default null, 
                  regexp text default null, `state` text default null)
               """)

    def add_user(self, chat_id, group):
        self.cursor.execute(f'INSERT INTO users (chat_id, `group`) VALUES ("{chat_id}", "{group}")')
        self.conn.commit()

    def get_group_by_password(self, password):
        sql = "SELECT `name` FROM `group` WHERE password=?"
        self.cursor.execute(sql, [password])
        val = self.cursor.fetchone()
        return val[0] if val else None

    def get_urls_by_chat_id(self, chat_id):
        _, group = self.find_user(chat_id)
        sql = "SELECT * FROM url"
        self.cursor.execute(sql)
        urls = self.cursor.fetchall()
        if group == 'all':
            return urls
        else:
            result = []
            for name, url, groups, online, xpath, regexp, state in urls:
                if group in json.loads(groups):
                    result.append((name, url, groups, online, xpath, regexp, state))
            return result

    def get_all_urls(self):
        sql = "SELECT * FROM url"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def find_chats_by_groups(self, groups):
        groups = '", "'.join(groups)
        sql = f'SELECT `chat_id` FROM users WHERE `group` IN ("{groups}") or `group`="all"'
        self.cursor.execute(sql)
        result = []
        for user in self.cursor.fetchall():
            result.append(user[0])
        return result

    def update_url_status(self, name, status):
        self.cursor.execute(f'UPDATE url SET online={status} WHERE `name`="{name}"')
        self.conn.commit()

    def update_url_status_state(self, name, state):
        self.cursor.execute(f'UPDATE url SET `state`="{state}" WHERE `name`="{name}"')
        self.conn.commit()

    def get_config_value(self, name, chat_id):
        sql = "SELECT `value` FROM config WHERE chat_id=? AND `name`=?"
        self.cursor.execute(sql, [chat_id, name])
        val = self.cursor.fetchone()
        return val[0] if val else None

    def add_config(self, name, value, chat_id):
        self.cursor.execute('INSERT INTO config VALUES ("{}", "{}", {})'.format(name, value, chat_id))
        self.conn.commit()

    def find_user(self, chat_id):
        sql = "SELECT * FROM users WHERE chat_id=?"
        self.cursor.execute(sql, [chat_id])
        return self.cursor.fetchone()

    def delete_user(self, chat_id):
        self.cursor.execute("DELETE FROM `users` WHERE chat_id=?", [chat_id])
        self.conn.commit()

    def update_config(self, name, value, chat_id):
        self.delete_config(name, chat_id)
        self.add_config(name, value, chat_id)

    def delete_config(self, name, chat_id):
        self.cursor.execute("DELETE FROM config WHERE chat_id=? AND `name`=?", [chat_id, name])
        self.conn.commit()

    def delete_all_config(self, chat_id):
        self.cursor.execute("DELETE FROM config WHERE chat_id=?", [chat_id])
        self.conn.commit()

    def get_configs(self, chat_id):
        sql = "SELECT * FROM config WHERE chat_id=?"
        self.cursor.execute(sql, [chat_id])
        return self.cursor.fetchall()
