import requests
from credentials import Credentials
import mysql.connector as mysql
import time


def authorize(code):
    r = requests.post("https://www.strava.com/oauth/token?client_id=" + str(Credentials.client_id) +
                      "&client_secret=" + str(Credentials.client_secret) +
                      "&code=" + str(code) +
                      "&grant_type=authorization_code")
    if r.ok:
        data = r.json()
        if "expires_at" in data and "token_type" in data \
                and "refresh_token" in data and "access_token" in data \
                and "athlete" in data and "id" in data["athlete"]:

            # print(data["expires_at"])
            # print(data["token_type"])
            # print(data["refresh_token"])
            # print(data["access_token"])
            # print(data["athlete"]["id"])
            # print(data["athlete"])

            if data["athlete"]["id"] == Credentials.user_id:

                db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                                   database=Credentials.database)
                cursor = db.cursor()
                cursor.execute("INSERT INTO user_credentials (id, refresh_token, access_token, expires_at) "
                               "VALUES (%s, %s, %s, %s) "
                               "ON DUPLICATE KEY "
                               "UPDATE refresh_token  = VALUES(refresh_token), "
                               "access_token   = VALUES(access_token), "
                               "expires_at   = VALUES(expires_at) ;",
                               (Credentials.user_id, data["refresh_token"], data["access_token"],
                                data["expires_at"])
                               )
                db.commit()
                db.disconnect()
                return True
            else:
                print("Wrong User")
                return False

    return False

def get_token(user_id=Credentials.user_id):
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database)
    cursor = db.cursor()
    cursor.execute("SELECT refresh_token, access_token, expires_at FROM user_credentials WHERE id=%s;", (user_id,))
    result = cursor.fetchone()
    if result and len(result) == 3:
        # print(result[0])
        # print(result[1])
        # print(result[2])
        # print(time.time())

        if float(result[2]) <= time.time():
            print("REFRESHING TOKEN...")
            return refresh(result[0])
        else:
            return result[1]
    return False


def refresh(refresh_token):
    r = requests.post("https://www.strava.com/oauth/token?client_id=" + str(Credentials.client_id) +
                      "&client_secret=" + str(Credentials.client_secret) +
                      "&refresh_token=" + str(refresh_token) +
                      "&grant_type=refresh_token")
    if r.ok:
        data = r.json()
        if "expires_at" in data and "token_type" in data \
                and "refresh_token" in data and "access_token" in data:
            # print(data["expires_at"])
            # print(data["token_type"])
            # print(data["refresh_token"])

            db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                               database=Credentials.database)
            cursor = db.cursor()
            cursor.execute("UPDATE user_credentials SET "
                           "refresh_token = %s, "
                           "access_token = %s, "
                           "expires_at = %s "
                           "WHERE id = %s;", (data["refresh_token"], data["access_token"],
                                              data["expires_at"], Credentials.user_id,))
            db.commit()
            db.disconnect()
            return data["access_token"]

    return False

# print(get_token())