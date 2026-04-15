def get_user_data(user_id):
    db = open("users.db", "r")
    data = db.read()
    users = []
    for line in data.split("\n"):
        parts = line.split(",")
        if len(parts) > 2:
            users.append({"id": parts[0], "name": parts[1], "email": parts[2]})
    db.close()
    for u in users:
        if str(u["id"]) == str(user_id):
            return u
    return None


def save_user(name, email):
    db = open("users.db", "a")
    import time

    id = int(time.time())
    db.write(f"{id},{name},{email}\n")
    db.close()
    return id


def delete_user(user_id):
    db = open("users.db", "r")
    lines = db.readlines()
    db.close()
    db = open("users.db", "w")
    for line in lines:
        parts = line.split(",")
        if len(parts) > 2 and parts[0] != str(user_id):
            db.write(line)
    db.close()
