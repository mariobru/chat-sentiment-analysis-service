#!/usr/bin/python3
from bottle import route, run, get, post, request
import psycopg2
import json
import os
import random
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from textblob import TextBlob 

# Connection to Postgresql in Heroku:
URL = 'postgres://ybgqdfwrfktliz:ed949a4fa7a88c55fc89844f3376c3aa59c4d64bde80a54b78b45d8397591960@ec2-46-137-113-157.eu-west-1.compute.amazonaws.com:5432/dckopqv6o4em74'
conn = psycopg2.connect(URL, sslmode='require')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

@get("/")
def index():
    return {
        "chatAPI": random.choice(["Create users!", "Add Messages"])
    }

@get("/<table>")
def selectTables(table):
    if table == "users":
        query = """SELECT * FROM users;"""
        cur.execute(query)
        result = cur.fetchall()
        return json.dumps(result)
    elif table == "messages":
        query = """SELECT * FROM messages;"""
        cur.execute(query)
        result = cur.fetchall()
        return json.dumps(result)
    elif table == "chats":
        query = """SELECT * FROM chats;"""
        cur.execute(query)
        result = cur.fetchall()
        return json.dumps(result)
    elif table == "iduser":
        query = """select iduser from users order by iduser desc limit 1;"""
        cur.execute(query)
        result = cur.fetchall()
        print(int(result[0][0])+1)
        return json.dumps(result) 

@get("/chat/<chat_id>/list")
def chatMessages(chat_id):
    chatid = int(chat_id)
    query = """SELECT text FROM messages WHERE chats_idchat={};""".format(chatid)
    cur.execute(query)
    result = cur.fetchall()
    return json.dumps(result)

@get("/chat/<chat_id>/showconv")
def chatConv(chat_id):
    chatid = int(chat_id)
    query = """select u.username, m.text from users u inner join messages m on u.iduser = m.users_iduser where m.chats_idchat={};""".format(chatid)
    cur.execute(query)
    result = cur.fetchall()
    return json.dumps(result)

@get("/chat/<chat_id>/sentiment")
def chatSent(chat_id):
    myjson = chatMessages(chat_id)
    messages = json.loads(myjson)
    polarity = 0
    subjectivity = 0
    for e in messages:
        polarity += TextBlob(*e).sentiment[0]
        subjectivity += TextBlob(*e).sentiment[1]
    polarity_mean = polarity/len(messages)
    subjectivity_mean = subjectivity/len(messages)
    return {
        'Polarity': 'is a float value within the range [-1.0 to 1.0] where 0 indicates neutral, +1 indicates a very positive sentiment and -1 represents a very negative sentiment.',
        'Subjectivity': 'is a float value within the range [0.0 to 1.0] where 0.0 is very objective and 1.0 is very subjective. Subjective sentence expresses some personal feelings, views, beliefs, opinions, allegations, desires, beliefs, suspicions, and speculations where as Objective sentences are factual.',
        'Polarity mean of this chat': polarity_mean, 
        'Subjectivity mean of this chat': subjectivity_mean
        }

@get("/user/<user_id>/listmessages")
def userMessages(user_id):
    query = """SELECT text FROM messages WHERE users_iduser={};""".format(user_id)
    cur.execute(query)
    result = cur.fetchall()
    return json.dumps(result)

@get('/user/create')
def insert_name():
    return '''<form method="POST" action="/user/create">
                Insert a new name: <input name="name"     type="text" />
                <input type="submit" />
              </form>'''

@post('/user/create')
def createUser():
    name = str(request.forms.get("name"))
    try:
        print(name)
        query = """SELECT username FROM users WHERE username='{}'""".format(name)
        cur.execute(query)
        dbname = cur.fetchone()[0]
        print(dbname)
    except:hat/7/showconvame already exists! Try a new one ;)"})
    else:
        query = """SELECT iduser FROM users ORDER BY iduser DESC limit 1;"""
        cur.execute(query)
        result = cur.fetchall()
        iduser = int(result[0][0]) + 1
        query = """INSERT INTO users (iduser, username) VALUES ({}, '{}') RETURNING {};""".format(iduser, name, 'users.iduser')
        cur.execute(query)
        id = cur.fetchone()[0]
        print(id)
        return json.dumps(id)

@post('/chat/create')
def createChat():
    query = """select idchat from chats order by idchat desc limit 1;"""
    cur.execute(query)
    result = cur.fetchall()
    idchat = int(result[0][0]) + 1
    query = """INSERT INTO chats (idchat) VALUES ({}) RETURNING {};""".format(idchat,'chats.idchat')
    cur.execute(query)
    id = cur.fetchone()[0]
    print("New chat created with chatid:",id)
    return json.dumps(id)

@get('/chat/addmessage')
def insert_message():
    return '''<form method="POST" action="/chat/addmessage">
                Insert a user id: <input name="userid"     type="text" />
                Insert a chat id: <input name="chatid"     type="text" />
                Send a comment to the chat: <input name="message"     type="text" />
                <input type="submit" />
              </form>'''

@post('/chat/addmessage')
def addMessage():
    chats_idchat = int(request.forms.get("chatid"))
    userid = int(request.forms.get("userid"))
    text = str(request.forms.get("message"))
    print(chats_idchat, userid)
    query = """select idmessage from messages order by idmessage desc limit 1;"""
    cur.execute(query)
    result = cur.fetchall()
    idmessage = int(result[0][0]) + 1
    query = """INSERT INTO messages (idmessage, text, datetime, users_iduser, chats_idchat) VALUES ({}, '{}', to_char(current_timestamp, 'yyyy-mm-dd hh24:mi:ss'), {}, {}) RETURNING {};""".format(idmessage, text, userid, chats_idchat, 'messages.idmessage')
    cur.execute(query)
    id = cur.fetchone()[0]
    print(id)
    return json.dumps(id)

port = int(os.getenv("PORT", 8080))
print(f"Running server {port}....")

run(host="0.0.0.0", port=port, debug=True)
