
chat_id = 43
token = ""
PATH_DATABASE = "database.db"


def get_admins():
    admin = chat_id
    if admin >= 1:
        admin = [admin]
    else:
        admin = []

    admin = list(map(int, admin))

    return admin
