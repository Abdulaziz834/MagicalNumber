import sqlite3

class DB_Control:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    

    def get_users(self):
        with self.conn:
            return self.cursor.execute("SELECT * FROM `user`")
    
    def add_user(self, user_id, first_name, last_name, username):
        with self.conn:
            return self.cursor.execute("INSERT INTO `user` (`user_id`, `first_name`, `last_name`, `username`) VALUES(?,?,?,?)", (user_id, first_name, last_name, username))
    
    def user_exist(self, user_id):
        with self.conn:
            result = self.cursor.execute('SELECT * FROM `user` WHERE `user_id` = ?', (user_id, )).fetchone()
            return bool((result))


    def update_user_data(self, user_id, first_name, last_name, username):
        with self.conn:
            return self.cursor.execute("UPDATE `user` SET `first_name` = ?, `last_name` = ?, `username` = ? WHERE `user_id` = ?", (first_name, last_name, username, user_id))
        
    def group_exist(self, chat_id):
        with self.conn:
            result = self.cursor.execute('SELECT * FROM `group` WHERE `group_id` = ?', (chat_id, )).fetchone()
            return bool((result))
        
    def add_group(self, group_id, group_name, group_lang):
        with self.conn:
            return self.cursor.execute("INSERT INTO `group` (`group_id`, `name`, `group_lang`) VALUES(?,?,?)", (group_id, group_name, group_lang))

    
    def update_group_data(self, group_id, group_name, group_lang):
        with self.conn:
            return self.cursor.execute("UPDATE `group` SET `name` = ?, `group_lang` = ? WHERE `group_id` = ?", (group_name, group_lang, group_id))
    
    def get_group_by_id(self, group_id):
        with self.conn:
            return self.cursor.execute("SELECT * FROM `group` WHERE `group_id` = ?", (group_id, ))


    def get_user_by_id(self, user_id):
        with self.conn:
            return self.cursor.execute("SELECT * FROM `user` WHERE `user_id` = ?", (user_id, ))

    def get_in_chats_user(self, chat_id):
        with self.conn:
            return self.cursor.execute("SELECT * FROM `group_user` WHERE `group_id` = ?", (chat_id, ))

    def get_top_gamers(self, chat_id, user_id):
        with self.conn:
            return self.cursor.execute("SELECT * FROM (SELECT *, ROW_NUMBER() OVER(Order by score DESC) as place FROM group_user WHERE group_id = ? ORDER BY score DESC) WHERE place < 4 OR user_id = ?", (chat_id, user_id)).fetchall()

    def group_user_exist(self, user_id, chat_id):
        with self.conn:
            result = self.cursor.execute("SELECT * FROM `group_user` WHERE `group_id` = ? AND `user_id` = ?", (chat_id, user_id)).fetchone()
            return bool(result)
        
    def add_group_user(self, group_id, user_id):
        with self.conn:
            return self.cursor.execute("INSERT INTO `group_user` (`group_id`, `user_id`, `score`) VALUES(?,?,?)", (group_id, user_id, 0))

    def get_group_user(self, group_id, user_id):
        with self.conn:
            return self.cursor.execute("SELECT * FROM `group_user` WHERE `group_id` = ? AND `user_id` = ?", (group_id, user_id))

    def change_user_score(self, user_id, score, chat_id):
        with self.conn:
            return self.cursor.execute("UPDATE `group_user` SET `score` = ? WHERE `user_id` = ? AND `group_id` = ?", (score, user_id, chat_id))

    def close(self):
        self.conn.close()