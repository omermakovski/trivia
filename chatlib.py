# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
MSG_DELIMITER="#"

# Protocol Messages
# In this dictionary we will have all the client and server command names
#COMMANDS= ["LOGIN","LOGOUT"]
PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "my_score_msg":"MY_SCORE",
     "get_question_msg": "GET_QUESTION",
    "send_answer_msg":"SEND_ANSWER",
    "logged_msg":"LOGGED",
    "get_high_score_msg": "HIGHSCORE"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR",
    "question_msg":"YOUR_QUESTION",
    "no_questions_msg":"NO_QUESTIONS",
    "correct_answer_msg":"CORRECT_ANSWER",
    "wrong_answer_msg":"WRONG_ANSWER",
    "all_score_msg":"ALL_SCORE",
    "answer_logged_msg":"LOGGED_ANSWER",
    "error_msg":"ERROR",
    "your_score_msg":"YOUR_SCORE"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error

import chatlib


def elimnate_spaces(msg):
    msg=msg.replace(" ", "")
    return msg

def build_message(cmd, data):
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occured
    """
    # Implement code ...
    filler = "0"
    spaces =(CMD_FIELD_LENGTH-len(cmd))*" "
    if (cmd not in PROTOCOL_CLIENT.values() and cmd not in PROTOCOL_SERVER.values()) or len(data)>MAX_DATA_LENGTH:
        return  ERROR_RETURN
    full_msg= cmd+spaces+DELIMITER+f'{len(data):{filler}{LENGTH_FIELD_LENGTH}}'+DELIMITER+data
    return full_msg


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    # Implement code ...

    # The function should return 2 values
    parts = data.split(DELIMITER)
    start = parts[0]
    cmd=elimnate_spaces(start)
    if (cmd not in PROTOCOL_CLIENT.values() and cmd not in PROTOCOL_SERVER.values()) or len(start)>CMD_FIELD_LENGTH or len(parts)<3 or len(data)>MAX_MSG_LENGTH:
        return (ERROR_RETURN,ERROR_RETURN)
    number=parts[1]
    try :
        number = int(number)
        if number<0 or number>MAX_DATA_LENGTH:
            return (ERROR_RETURN, ERROR_RETURN)
    except:
        return (ERROR_RETURN,ERROR_RETURN)
    msg1=""
    for i in range(2,len(parts)):
        msg1+=parts[i]+DELIMITER
    #print(msg1[:-1])
    msg2=data[-number:]
    if msg1[:-1]!=msg2 and number!=0:
        return (ERROR_RETURN, ERROR_RETURN)
    return cmd, msg1[:-1]


def split_msg(msg, expected_fields,delimiter_for_you):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    msg_fields = msg.split(delimiter_for_you)
    if len(msg_fields)==expected_fields:
        return msg_fields
    else:
        return ERROR_RETURN

# Implement code ...


def join_msg(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the delimiter.
    Returns: string that looks like cell1|cell2|cell3
    """
# Implement code ...
    msg=""
    for cell in msg_fields:
        try:
            msg+=cell+DELIMITER
        except:
            return ERROR_RETURN
    return msg[:-1]


