##############################################################################
# server.py
##############################################################################
#imports
import socket
import chatlib
import random
import select

# GLOBALS
users = {}
questions = {}
logged_users = {}
data_queue ={}
messages_to_send = []
client_sockets = []

COMMANDS = ["LOGIN", "LOGOUT", "MY_SCORE","GET_QUESTION","SEND_ANSWER","LOGGED","HIGHSCORE"]
ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS
#builds amessage and adds it to messages to send
def build_and_send_message(conn, code, msg):
    global messages_to_send
    final_msg = chatlib.build_message(code, msg)
    #print(f"Interpretation for what we sent:\nCommand: {code}, message: {msg}")
    if final_msg != chatlib.ERROR_RETURN:
        print("[SERVER] ", final_msg)  # Debug print
        messages_to_send.append((conn,final_msg))



#recives data from a client and gets the message and command
def recv_message_and_parse(conn):
    try:
        data = conn.recv(10021).decode()
    except:
        return "",""
    cmd, msg = chatlib.parse_message(data)
    if cmd == chatlib.ERROR_RETURN or msg == chatlib.ERROR_RETURN:
        return ("","")
    elif cmd != chatlib.ERROR_RETURN or msg != chatlib.ERROR_RETURN:
        #print(f"The client sent: {data}")
        print("[CLIENT] ", cmd, msg)  # Debug print
        #print(f"Interpretation for what we recived:\nCommand: {cmd}, message: {msg}")
        return cmd, msg
    else:
        return chatlib.ERROR_RETURN, chatlib.ERROR_RETURN

    # Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    #questions = {
    #    2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
    #    4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
    #           "correct": 3}
    #}

    questions = open("questions.txt")
    questions = questions.read()
    questions = questions.split("\n")
    final_questions = {}
    for question in questions:
        fildes = {}
        arr = question.split('|')
        if len(arr) == 6:
            question1 = arr[0]
            answers = [arr[1], arr[2], arr[3], arr[4]]
            correct = int(arr[5])
            fildes["question"] = question1
            questions = arr[3]
            fildes["answers"] = answers
            fildes["correct"] = correct
            question_id = random.randint(1, 10000)
            final_questions[question_id] = fildes
    return final_questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    #users = {
    #    "test"	:	{"password" :"test" ,"score" :0 ,"questions_asked" :[]},
    #    "yossi"		:	{"password" :"123" ,"score" :50 ,"questions_asked" :[]},
    #    "master"	:	{"password" :"master" ,"score" :200 ,"questions_asked" :[]}
    #}
    users = open("users.txt")
    users = users.read()
    users = users.split("\n")
    final_users = {}
    for user in users:
        fildes = {}
        arr = user.split('|')
        if len(arr) == 4:
            username = arr[0]
            fildes["password"] = arr[1]
            fildes["score"] = int(arr[2])
            questions = arr[3]
            if len(questions) == 0:
                questions_asked = []
            else:
                questions_asked = questions.split(',')
            fildes["questions_asked"] = questions_asked
            final_users[username] = fildes
    #print(final_users)
    return final_users



# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    # Implement code ...
    server_socket = socket.socket()
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Server is up and running")
    return server_socket


#sends each command to their function
def what_to_do(command,conn,data):
    username = logged_users[tuple(conn.getpeername())]
    if command==COMMANDS[0]:
        handle_login_message(conn, data)
    elif command == COMMANDS[1]:
        handle_logout_message(conn)
    elif command == COMMANDS[2]:
        handle_getscore_message(conn, username)
    elif command == COMMANDS[3]:
        handle_question_message(conn,username)
    elif command == COMMANDS[4]:
        handle_answer_message(conn,username,data)
    elif command == COMMANDS[5]:
        handle_logged(conn)
    elif command == COMMANDS[6]:
        handle_get_highscore(conn)


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    cmd=chatlib.PROTOCOL_SERVER["error_msg"]
    build_and_send_message(conn,cmd,error_msg)
# Implement code ...




##### MESSAGE HANDLING
#handles a get score message
def handle_getscore_message(conn, username):
    global users
    score = (users[username])["score"]
    print(score)
    if score=='':
        score="0"
    cmd = chatlib.PROTOCOL_SERVER["your_score_msg"]
    build_and_send_message(conn,cmd,str(score))

#handles get highscore message
def handle_get_highscore(conn):
    global logged_users
    global users

    logged_users_name = logged_users.values()
    users_scores =  {}
    for name in logged_users_name:
        users_scores[name]=users[name]["score"]
    sort_users_scores = sorted(users_scores.items(), key=lambda x: x[1], reverse=True)
    msg = ""
    for tup in sort_users_scores:
        msg+=tup[0]+":"+str(tup[1])+"\n"
    cmd =chatlib.PROTOCOL_SERVER["all_score_msg"]
    build_and_send_message(conn,cmd,msg)

#handles logged message
def handle_logged(conn):
    global logged_users
    logged_users_name = logged_users.values()
    msg=""
    for user in logged_users_name:
        msg+=user+", "
    msg=msg[:-2]
    cmd = chatlib.PROTOCOL_SERVER["answer_logged_msg"]
    build_and_send_message(conn,cmd,msg)

#handles logout message
def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    global client_sockets

    client_sockets.remove(conn)
    del(logged_users[tuple(conn.getpeername())])
    conn.close()

#handles login message
def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users	 # To be used later
    user_id =  chatlib.split_msg(data, 2, "#")
    if tuple(conn.getpeername()) in logged_users.keys():
        send_error("the user is already logged in")
        return
    if user_id ==chatlib.ERROR_RETURN:
        send_error(conn,"client sent ileagell username and password")
        return
    client_name = user_id[0]
    client_password1 = user_id[1]
    if client_name not in users.keys():
        send_error(conn, "client sent wrong user name")
        return
    client_data = users[client_name]
    client_password2 = client_data["password"]
    if client_password1!=client_password2:
        send_error(conn, "client sent wrong password")
        return
    logged_users[tuple(conn.getpeername())] = client_name
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "")

#handles question message
def handle_question_message (conn,username):
    msg = create_random_question(username)
    if msg==None:
        cmd=chatlib.PROTOCOL_SERVER["no_questions_msg"]
        build_and_send_message(conn,cmd,"")
        return
    good_cmd =  chatlib.PROTOCOL_SERVER["question_msg"]
    build_and_send_message(conn, good_cmd, msg)

#handles answer message
def handle_answer_message(conn,username,answer):
    qst_ans = answer.split("#")
    if len(qst_ans)!=2:
        send_error(conn,"the client sent an illeagel answer")
    question_id = qst_ans[0]
    if int(question_id) not in questions.keys():
        send_error(conn,"the client sent an illeagel question id")
    client_answer = qst_ans[1]
    if client_answer not in ["1","2","3","4"]:
        send_error(conn,"the client sent an illeagel answer")
    right_answer = str(questions[int(question_id)]["correct"])
    if right_answer!=client_answer:
        cmd = chatlib.PROTOCOL_SERVER["wrong_answer_msg"]
        build_and_send_message(conn,cmd,right_answer)
    else:
        cmd = chatlib.PROTOCOL_SERVER["correct_answer_msg"]
        users[username]["score"]+=5
        build_and_send_message(conn,cmd,"")

#handles the clients message
def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users

    if tuple(conn.getpeername()) in logged_users.keys():
        if cmd not in COMMANDS:
            send_error(conn,"the client sent a command we dont know")
        elif cmd==  cmd == COMMANDS[0]:
            send_error(conn,"A logged user asked to login")
        else:
            what_to_do(cmd,conn,data)
    else:
        if cmd == COMMANDS[0]:
            handle_login_message(conn, data)
        else:
            send_error(conn,"the client sent a command while not logged in")

#creates a random question for the function that handels question message
def create_random_question(username):
    questions_askes = (users[username])["questions_asked"] #arr with id of question
    questions_for_user = questions.keys()
    questions_left = list(set(questions_for_user) - set(questions_askes))
    if len(questions_left)==0:
        return None
    your_question_id = questions_left[random.randint(0,len(questions_left)-1)]
    users[username]["questions_asked"].append(your_question_id)
    question = questions[your_question_id]
    answers = question["answers"]
    msg = str(your_question_id)+chatlib.MSG_DELIMITER+question["question"]+chatlib.MSG_DELIMITER
    for answer in answers:
        msg+=answer+chatlib.MSG_DELIMITER
    return msg[:-1]

#prints all logged clients sockets
def print_client_sockets():
    global logged_users
    print("the logged users are:")
    for user in logged_users.keys():
        print(user)

#sends all waiting messages
def send_waiting_messages(wlist):
    global messages_to_send
    for message in messages_to_send:
        current_socket, data = message
        if current_socket in wlist:
            current_socket.send(data.encode())
        messages_to_send.remove(message)

#def add_message_to_queue(conn,data):
 #   global data_queue
 #   key = tuple(conn.getpeername())
 #   if key in data_queue.keys:
 #       data_queue[key]+=str(data)
 #   else :
 #       data_queue[key] = str(data)


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global data_queue
    global logged_users
    global client_sockets

    print("Welcome to Trivia Server!")
    our_socket = setup_socket()
    users = load_user_database()
    questions = load_questions()

    while True:
        read_list = [our_socket] + client_sockets
        ready_to_read, ready_to_write, in_error = select.select(read_list,client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is our_socket:
                (client_socket, client_address) = our_socket.accept()
                print(f"new client connected: {client_address}")
                client_sockets.append(client_socket)
            else:
                print("new data from client")
                #data_queue[current_socket.getpeername()] = 1#מידע שהתקבל עבור הסוקט
                cmd, msg = recv_message_and_parse(current_socket)
                if cmd=="" and msg=="":
                    del(logged_users[tuple(current_socket.getpeername())])
                    ready_to_write.remove(current_socket)
                    client_sockets.remove(current_socket)
                    current_socket.close()
                else:
                    handle_client_message(current_socket,cmd,msg)
        send_waiting_messages(ready_to_write)
    our_socket.close()
# Implement code ...



if __name__ == '__main__':
    main()

