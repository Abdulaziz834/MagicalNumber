#!/usr/bin/python3.10.0
# -*- coding: utf-8 -*-from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from random import randint, sample
from db_manager import DB_Control
from message import messages
from time import sleep

db = DB_Control('bot.sqlite')

GAMES = {}
BTN_EN_JOIN, BTN_RU_JOIN = InlineKeyboardMarkup([[InlineKeyboardButton(
    "➕ Join to the game 🎮", callback_data="join")]]), InlineKeyboardMarkup([[InlineKeyboardButton(
    "➕ Присоединиться к игре 🎮", callback_data="join")]])
BTNS_LANG = InlineKeyboardMarkup([[InlineKeyboardButton(
    "🇺🇸 English 🇺🇸", callback_data="en")], [InlineKeyboardButton(
    "🇷🇺 Русский 🇷🇺", callback_data="ru")]])


def is_group(chat_type):
    return chat_type.message.chat.type == "supergroup" or chat_type.message.chat.type == "group"

def is_group_admin(user_id, admin_list):
    for admin in admin_list:
        if (admin.user.id == user_id):
            return True
    return False

def mention_name(player_id):
    player1 = db.get_user_by_id((player_id))
    for x in player1:
        player = dict(x)

    return "<a href='tg://user?id={}'>{}</a>".format(player["user_id"], player["first_name"])


def start(update, context):
    user = update.effective_user
    chat_id = update.message.chat_id
    if is_group(update):
        context.bot.send_message(chat_id=chat_id, text=f"Hello <b>{user.first_name}</b>, choose your language 👇\n\nПривет <b>{user.first_name}</b>, выберите свой язык 👇", reply_markup=BTNS_LANG, parse_mode="html")
    else:
        context.bot.send_message(chat_id=chat_id, text=f"Hello <b>{update.message.chat.title}</b>, choose your language for chat 👇\n\nПривет <b>{update.message.chat.title}</b>, выберите свой язык для чата 👇", reply_markup=BTNS_LANG, parse_mode="html")

def get_lang(chat_id):
    for k in db.get_group_by_id(chat_id):
        lang = dict(k)["group_lang"]
    return lang

def new_game(context):
    job = context.job
    chat_id = job.context["chat_id"]
    room = GAMES["room_"+str(chat_id)]
    lang = get_lang(chat_id)
    if (len(room["players"]) > 1):
        room["magic_number"] = randint(1, len(room["players"]) * 50)
        room["highest"] = len(room["players"]) * 50
        room["players"] = sample(room["players"], k=len(room["players"]))
        context.bot.delete_message(chat_id=chat_id, message_id=job.name)
        context.bot.send_message(text=messages[lang][5], chat_id=chat_id)
        player1 = db.get_user_by_id(room["players"][0])
        for x in player1:
            player = dict(x)
        sleep(1)
        context.bot.send_message(chat_id=chat_id, text=messages[lang][6].format(player["user_id"], player["first_name"], room["lowest"], room["highest"]), parse_mode="html")
    else:
        context.bot.delete_message(chat_id=chat_id, message_id=job.name)
        context.bot.send_message(text=messages[lang][7], chat_id=chat_id)
        GAMES.pop("room_" + str(chat_id))


def startgame(update, context):
    user = update.effective_user
    chat_id = update.message.chat_id
    if is_group(update):
        lang = None
    lang = get_lang(chat_id)
    if (not lang):
        context.bot.send_message(chat_id=chat_id, text="<b>Admins</b> of this group should register this group to bot.\nClick <b>/start</b> to register\n\n<b>Администраторы</b> этой группы должны зарегистрировать эту группу в боте.\nНажмите <b>/start</b>, чтобы зарегистрировать", parse_mode="html")
        return
    if (not GAMES.get("room_" + str(chat_id))):
        context.bot.send_message(chat_id=chat_id, text=messages[lang][2], reply_markup=BTN_EN_JOIN if lang == "en" else BTN_RU_JOIN, parse_mode="html")
        GAMES["room_" + str(chat_id)] = {"magic_number": 0, "players": [], "turn": 0, "lowest": 0, "highest": 0, "stop": {"is_stopping": False, "agree": [], "disagree": []}}

        context.job_queue.run_once(new_game, 30, context={"chat_id": chat_id}, name=str(update.message.message_id+1))
    else:
        context.bot.send_message(chat_id=chat_id, text=messages[lang][4], parse_mode="html")


def inline_handler(update, context):
    global BTN_JOIN
    query = update.callback_query
    user = query.from_user
    chat_id = str(query.message.chat.id)
    callback_data = query.data
    if (callback_data == "join"):
        lang = get_lang(chat_id)

        if not (db.user_exist(user.id)):
            db.add_user(user.id, user.first_name, user.last_name, user.username)
        else:
            db.update_user_data(user.id, user.first_name, user.last_name, user.username)
        if not (db.group_user_exist(user.id, chat_id)):
            db.add_group_user(chat_id, user.id)
        
        room = GAMES["room_"+chat_id]
        if not user.id in room["players"]:
            room["players"].append(user.id)
            query.edit_message_text(messages[lang][3] + "\n".join(list(map(mention_name, room["players"]))), reply_markup=BTN_EN_JOIN if lang == "en" else BTN_RU_JOIN, parse_mode="html")
        return
    if (is_group(query)):
        if (is_group_admin(user.id, context.bot.get_chat_administrators(chat_id))):
            query.edit_message_text(text=messages[callback_data][0].format(query.message.chat.title), parse_mode="html")
            if (not db.group_exist(chat_id)):
                db.add_group(chat_id, query.message.chat.title, callback_data)
            else:
                db.update_group_data(chat_id, query.message.chat.title, callback_data)
        else:
            context.bot.answer_callback_query(callback_query_id=query.id, text=messages[callback_data][1])



def showgames(update, context):
    user = update.effective_user
    if user.id == 1273666675:
        context.bot.send_message(chat_id = user.id, text=f'<pre><code class="language-python">{GAMES}</code></pre>', parse_mode="html")


def turn_increment(turn, itera):
    if ((turn + 1) == len(itera)):
        return 0 
    return turn + 1


def topgamers(update, context):
    user = update.effective_user
    chat_id = update.message.chat_id
    if is_group(update):
        lang = get_lang(chat_id)
        top = ""
        medals = ["🥇", "🥈", "🥉"]
        for i, player in enumerate(db.get_top_gamers(chat_id, user.id)):
            player = dict(player)
            player_user = [dict(x) for x in db.get_user_by_id(player["user_id"])][0]
            if (player["place"] < 4):
                if (player["user_id"] == user.id):
                    top += "<i>{} {} - <b>{}</b></i>\n".format(medals[i], mention_name(player["user_id"]), player["score"])
                    continue
                top += "{} {} - <b>{}</b>\n".format(medals[i], player_user["first_name"], player["score"])
                continue
            else:
                top += "\n<i>#{} - {} - <b>{}</b></i>".format(player['place'], player_user["first_name"], player["score"])
        context.bot.send_message(chat_id=chat_id, text=messages[lang][14] + top, parse_mode="html")

def message_handler(update, context):
    user = update.effective_user
    chat_id = update.message.chat_id
    if (GAMES.get("room_" + str(chat_id))):
        room = GAMES.get("room_" + str(chat_id))
        text = update.message.text
        lang = get_lang(chat_id)
        if (user.id == room["players"][room["turn"]]):
            if (text.isdigit()):
                text = int(text)
                # if (room["stop"]["is_stopping"]):
                #     update.message.reply_html()
                if (room["magic_number"] == 0):
                    return
                if (room["highest"] < text or text < room["lowest"]):
                    update.message.reply_html(messages[lang][13].format(room["lowest"], room["highest"]))
                    return
                if (text > room["magic_number"]):
                    update.message.reply_html(messages[lang][8].format(str(text)))
                    room["turn"] = turn_increment(room["turn"], room["players"])
                    room["highest"] = text
                    for x in db.get_user_by_id(room["players"][room["turn"]]):
                        player = dict(x)
                    context.bot.send_message(chat_id=chat_id, text=messages[lang][6].format(player["user_id"], player["first_name"], room["lowest"], room["highest"]), parse_mode="html")
                elif (text < room["magic_number"]):
                    update.message.reply_html(messages[lang][9].format(str(text)))
                    room["turn"] = turn_increment(room["turn"], room["players"])
                    room["lowest"] = text
                    for x in db.get_user_by_id(room["players"][room["turn"]]):
                        player = dict(x)
                    context.bot.send_message(chat_id=chat_id, text=messages[lang][6].format(player["user_id"], player["first_name"], room["lowest"], room["highest"]), parse_mode="html")
                else:
                    for x in db.get_user_by_id(room["players"][room["turn"]]):
                        player = dict(x)
                    for l in db.get_group_user(chat_id, player["user_id"]):
                        group_user = dict(l)
                    update.message.reply_html(messages[lang][10].format(player["user_id"], player["first_name"], (int(group_user["score"]) + 1)))
                    db.change_user_score(player['user_id'], int(group_user["score"] + 1), chat_id)
                    GAMES.pop("room_" + str(chat_id))
            else:
                for x in db.get_user_by_id(room["players"][room["turn"]]):
                    player = dict(x)
                update.message.reply_html(messages[lang][11].format(player["user_id"], player["first_name"], room["lowest"], room["highest"]))
        else:
            if (text.isdigit()):
                
                context.bot.send_message(chat_id=chat_id, text=messages[lang][12].format(user.mention_html()), parse_mode="html")
                sleep(3)
                context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
                context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id+1)



def main():
    updater = Updater("5583073372:AAEpYrRNwZs0w0iUPgPZrMKfxGXOKKgGZVU", use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("startgame", startgame))
    dp.add_handler(CommandHandler("showgames", showgames))
    dp.add_handler(CommandHandler("topgamers", topgamers))
    dp.add_handler(CallbackQueryHandler(inline_handler))
    dp.add_handler(MessageHandler(Filters.text, message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()