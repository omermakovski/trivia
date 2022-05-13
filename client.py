import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678
CHOISES_TO_PLAY = ["score", "logout", "question", "logged", "highscore"]


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """

    final_msg=chatlib.build_message(code,msg)
    #print(final_msg)
    #print(f"Interpretation for what we sent:\nCommand: {code}, message: {msg}")
    if final_msg!=chatlib.ERROR_RETURN:
        final_msg = final_msg.encode()
        conn.send(final_msg)


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    # Implement Code
    # ..
    data = conn.recv(10021).decode()#10021
    #print("recived data")
    #print(data)
    cmd, msg = chatlib.parse_message(data)
    if cmd != chatlib.ERROR_RETURN or msg != chatlib.ERROR_RETURN:
        #print(f"The server sent: {data}")
        #print(f"Interpretation for what we recived:\nCommand: {cmd}, message: {msg}")
        return cmd, msg
    else:
        return chatlib.ERROR_RETURN, chatlib.ERROR_RETURN

    cmd, msg = chatlib.parse_message(data)
    return cmd, msg


def connect():
    # Implement Code
    new_socket =socket.socket()
    new_socket.connect((SERVER_IP, SERVER_PORT))
    print("connected socket")
    return new_socket


def error_and_exit(msg):
    # Implement code
    print(msg)
    exit()


def what_to_do(choise,new_socket):
    if choise==CHOISES_TO_PLAY[0]:
        get_score(new_socket)
    elif choise==CHOISES_TO_PLAY[1]:
        logout(new_socket)
    elif choise == CHOISES_TO_PLAY[2]:
        play_question(new_socket)
    elif choise == CHOISES_TO_PLAY[3]:
        get_logged_users(new_socket)
    elif  choise == CHOISES_TO_PLAY[4]:
        get_highscore(new_socket)

def login(conn):

    while True:
        username = input("Please enter username: \n")
        password = input("Please enter password: \n")
        msg = username+chatlib.MSG_DELIMITER+password
        build_and_send_message(conn,chatlib.PROTOCOL_CLIENT["login_msg"],msg)
        cmd, msg = recv_message_and_parse(conn)
        if cmd=="LOGIN_OK":
            print("connectaion was succesful")
            break
        print("connectaion was not succesful")



# Implement code



def logout(conn):
    # Implement code
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")

def build_send_recv_parse (conn,cmd,data):
    build_and_send_message(conn, cmd, data)
    return recv_message_and_parse(conn)

def get_score(conn):
     our_cmd=chatlib.PROTOCOL_CLIENT["my_score_msg"]
     data=""
     cmd,msg = build_send_recv_parse(conn,our_cmd,data)
     if cmd!="YOUR_SCORE" :
         error_and_exit("the server sent a wrong command")
     elif int(msg) % 5 != 0:
         error_and_exit("the score isnt devideball by 5")
     else:
         print(f"your score so far is {msg}\n")


def play_question(conn):
    cmd =chatlib.PROTOCOL_CLIENT["get_question_msg"]
    data=""
    recv_cmd,msg = build_send_recv_parse(conn, cmd, data)
    if msg==None:
        error_and_exit("there are no more questions")
        return
    elif recv_cmd== chatlib.PROTOCOL_SERVER["no_questions_msg"]:
        print("there are no more questions")
        return
    elif recv_cmd!= chatlib.PROTOCOL_SERVER["question_msg"]:
        error_and_exit("the server returned something wrong")
        return
    arr = msg.split("#")
    if len(arr)!=6:
        error_and_exit("there are to many # in the answer from the server")
        return
    question_index=arr[0]
    question = arr[1]
    print(f"the question is:\n{question}")
    print("the possible answers are")
    for i in range(1,5):
        print(f"{i}. {arr[i+1]}")
    while True:
        answer= input("enter yor answer (1,2,3,4) :")
        if answer in ["1","2","3","4"]:
            break
    cmd = chatlib.PROTOCOL_CLIENT["send_answer_msg"]
    data = str(question_index)+chatlib.MSG_DELIMITER+answer
    recv_cmd, msg = build_send_recv_parse(conn, cmd, data)

    if recv_cmd== chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
        print("you answered right")
    elif recv_cmd== chatlib.PROTOCOL_SERVER["wrong_answer_msg"] and msg in ["1","2","3","4"]:
        print(f"you answered wrong\nthe correct answer was {msg}. : {arr[int(msg)+1]}")
    else:
        error_and_exit("the server returned something wrong")
        return


def get_highscore(conn):
    cmd = chatlib.PROTOCOL_CLIENT["get_high_score_msg"]
    data=""
    recv_cmd, msg = build_send_recv_parse(conn, cmd, data)
    if recv_cmd!=chatlib.PROTOCOL_SERVER["all_score_msg"]:
        error_and_exit("the server returned something wrong")
    else:
        print(msg)

def get_logged_users (conn):
    cmd = chatlib.PROTOCOL_CLIENT["logged_msg"]
    data = ""
    recv_cmd, msg = build_send_recv_parse(conn, cmd, data)
    if recv_cmd!=chatlib.PROTOCOL_SERVER["answer_logged_msg"]:
        error_and_exit("the server returned something wrong")
    else:
        print(msg)

def main():
    # Implement code
    new_socket = connect()
    login(new_socket)
    while True:
        print("Enter what you would like to play next, your options:\nscore - see your score\nlogout - logging out\nquestion - playing a next question\nlogged - seeing all the logged in users\nhighscore - see the high score chart")
        choise = input("enter here: ")
        if choise not in CHOISES_TO_PLAY:
            print("you enterd something wrong try again")
        else:
            what_to_do(choise,new_socket)
        if choise==CHOISES_TO_PLAY[1]:
            break
    new_socket.close()



if __name__ == '__main__':
    main()