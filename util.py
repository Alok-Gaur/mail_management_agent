import base64

def decode_mail(data):
    pass

def store_start_history(historyId):
    with open("mail_history.txt", 'w') as file:
        file.write(historyId)

def get_start_history():
    with open("mail_history.txt", 'r') as file:
        historyId = int(file.read())
        return historyId
