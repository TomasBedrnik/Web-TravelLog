import requests
from credentials import Credentials
import mysql.connector as mysql
import datetime
from app import auth

def replace_smileys(text):
    dictionary = {":-)": "😀️", ":)": "☺️",
                  ":-D": "😀", ":D": "😀",
                  ";-)": "😉", ";)": "😉",
                  ":-P": "😛", ":P": "😛",
                  ";-P": "😜", ";P": "😜",
                  ":-|": "😐", ":|": "😐",
                  ":-/": "😕", ":/": "😕",
                  ":-\\": "😕", ":\\": "😕",
                  ":-(": "☹️", ":(": "☹️",
                  ":'‑(": "😢", ":'(": "😢"}

    for key in dictionary.keys():
        text = text.replace(key, dictionary[key])

    return text


def read_activity(activity_id):
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()

    cursor.execute("SELECT a.id, `user_id`, `upload_id`, `external_id`, `start_date_local`, `name`, `distance`, "
                   "`moving_time`, `elapsed_time`, `total_elevation_gain`, `type`, `description`, `total_photo_count`, "
                   "GROUP_CONCAT(p.id order by p.photo_order), GROUP_CONCAT(p.url_small order by p.photo_order), "
                   "GROUP_CONCAT(p.url_big order by p.photo_order), GROUP_CONCAT(p.caption order by p.photo_order) "
                   "FROM activities as a "
                   "LEFT JOIN photos as p ON a.id = p.activity_id "
                   "WHERE a.id='%s'", (activity_id,))
    data = cursor.fetchone()
    data = list(data)
    data[4] = datetime.datetime.strptime(data[4], "%Y-%m-%dT%H:%M:%SZ")
    data[7] = ':'.join(str(datetime.timedelta(seconds=data[7])).split(':')[:2])
    data[8] = ':'.join(str(datetime.timedelta(seconds=data[8])).split(':')[:2])
    # format output
    db.disconnect()
    return data


def read_activity_map(activity_id):
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("SELECT polyline FROM activities WHERE id='%s'", (activity_id,))
    data = cursor.fetchall()
    list_polyline = []
    for d in data:
        list_polyline.append(d[0])
    db.disconnect()
    return list_polyline


def read_comments(activity_id):
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("SELECT `id`, `date`, `name`, `text` FROM comments WHERE activity_id='%s' "
                   "order by `date` desc", (activity_id,))
    data = cursor.fetchall()
    db.disconnect()
    return data


def read_stats():
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("SELECT SUM(distance), SUM(moving_time), SUM(elapsed_time), SUM(total_elevation_gain) "
                   "FROM `activities` WHERE 1")

    data = cursor.fetchone()
    data = list(data)
    data_1_dny = False
    data_2_dny = False
    if len(data) > 0 and data[1] and data[2]:
        if data[1] < 4*24*60*60:
            data_1_dny = True
        if data[2] < 4*24*60*60:
            data_2_dny = True

        data[1] = ':'.join(str(datetime.timedelta(seconds=data[1])).split(':')[:2])
        data[2] = ':'.join(str(datetime.timedelta(seconds=data[2])).split(':')[:2])
        data[1] = data[1].replace("days", "dní").replace("day", "den")
        data[2] = data[2].replace("days", "dní").replace("day", "den")
        if data_1_dny:
            data[1] = data[1].replace("dní", "dny")
        if data_2_dny:
            data[2] = data[2].replace("dní", "dny")
        db.disconnect()
        return data


def read_activities():
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("SELECT a.id, `user_id`, `upload_id`, `external_id`, `start_date_local`, a.`name`, `distance`,"
                   "`moving_time`, `elapsed_time`, `total_elevation_gain`, `type`, `description`, `total_photo_count`,"
                   "t1.p_id, t1.small_p, t1.big_p, t1.caption_p, t2.num_comments "
                   "FROM activities as a "
                   "LEFT JOIN ( "
                   "    SELECT activity_id, GROUP_CONCAT(p.id order by p.photo_order) as p_id, "
                   "    GROUP_CONCAT(p.url_small order by p.photo_order) as small_p, "
                   "    GROUP_CONCAT(p.url_big order by p.photo_order) as big_p, "
                   "    GROUP_CONCAT(p.caption order by p.photo_order) as caption_p"
                   "    FROM photos as p"
                   "    GROUP by p.activity_id"
                   ") t1 ON a.id = t1.activity_id "
                   "LEFT JOIN ( "
                   "    SELECT activity_id, COUNT(distinct c.id) AS num_comments"
                   "    FROM comments as c"
                   "   GROUP by c.activity_id"
                   ") t2 ON a.id = t2.activity_id order by a.start_date_local desc ")
    data = cursor.fetchall()
    db.disconnect()
    # format output
    for i, val in enumerate(data):
        data[i] = list(val)
        data[i][4] = datetime.datetime.strptime(val[4], "%Y-%m-%dT%H:%M:%SZ")
        data[i][7] = ':'.join(str(datetime.timedelta(seconds=val[7])).split(':')[:2])
        data[i][8] = ':'.join(str(datetime.timedelta(seconds=val[8])).split(':')[:2])

    if len(data) > 0:
        # remove last activity until next day morning 8:30
        tmp_date = data[0][4].replace(hour=8, minute=30) + datetime.timedelta(days=1)
        if datetime.datetime.now() < tmp_date:
            data.pop(0)
    return data


def read_activities_map():
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("SELECT start_date_local, polyline FROM activities order by start_date_local desc")
    data = cursor.fetchall()

    if len(data) > 0:
        # remove last activity until next day morning 8:30
        tmp_date = datetime.datetime.strptime(data[0][0], "%Y-%m-%dT%H:%M:%SZ").replace(hour=8, minute=30) + \
                   datetime.timedelta(days=1)
        if datetime.datetime.now() < tmp_date:
            data.pop(0)

    list_polyline = []
    for d in data:
        list_polyline.append(d[1])
    db.disconnect()
    return list_polyline


def add_comment(activity_id, name, text):
    text = replace_smileys(text)
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("INSERT INTO comments (`activity_id`, `date`, `name`, `text`) VALUES (%s, %s, %s, %s)",
                   (activity_id, datetime.datetime.now(), name, text))
    db.commit()
    db.disconnect()


def update_photos(user_id, cursor, headers):
    r3 = requests.get("https://www.strava.com/api/v3/activities/" + str(user_id) +
                      "/photos?photo_sources=true&size=200", headers=headers)
    r4 = requests.get("https://www.strava.com/api/v3/activities/" + str(user_id) +
                      "/photos?photo_sources=true&size=30000", headers=headers)

    if r3.ok and r4.ok:
        data3 = r3.json()
        data4 = r4.json()
        if len(data3) == len(data4):
            for i in range(len(data3)):
                cursor.execute("INSERT INTO photos (`id`, `activity_id`, `caption`, `url_small`, "
                               "`url_big`) "
                               "VALUES (%s, %s, %s, %s, %s) "
                               "ON DUPLICATE KEY "
                               "UPDATE "
                               "id  = VALUES(id), "
                               "activity_id   = VALUES(activity_id), "
                               "caption   = VALUES(caption), "
                               "url_small   = VALUES(url_small), "
                               "url_big   = VALUES(url_big) ;",
                               (data3[i]["unique_id"], data3[i]["activity_id"],
                                data3[i]["caption"], data3[i]["urls"]["200"],
                                data4[i]["urls"]["30000"])
                               )



def delete_activity(activity_id):
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    cursor.execute("DELETE FROM activities WHERE id='%s'; ", (activity_id,))
    cursor.execute("DELETE FROM photos WHERE activity_id='%s'; ", (activity_id,))
    db.commit()
    db.disconnect()


def update_activity(user_id, cursor, headers):
    r = requests.get("https://www.strava.com/api/v3/activities/" + str(user_id), headers=headers)
    if r.ok:
        data = r.json()
    if "summary_polyline" not in data["map"].keys():
        return
    text = replace_smileys(data["description"])

    cursor.execute("INSERT INTO activities (`id`, `user_id`, `upload_id`, `external_id`, "
                   "`start_date_local`, `name`, `distance`, `moving_time`, `elapsed_time`, "
                   "`total_elevation_gain`, `type`, `description`,`polyline`,`summary_polyline`, "
                   "`total_photo_count`) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                   "ON DUPLICATE KEY "
                   "UPDATE "
                   "id  = VALUES(id), "
                   "user_id   = VALUES(user_id), "
                   "upload_id   = VALUES(upload_id), "
                   "external_id   = VALUES(external_id), "
                   "start_date_local   = VALUES(start_date_local), "
                   "`name`   = VALUES(`name`), "
                   "distance   = VALUES(distance), "
                   "moving_time   = VALUES(moving_time), "
                   "elapsed_time   = VALUES(elapsed_time), "
                   "total_elevation_gain   = VALUES(total_elevation_gain), "
                   "`type`   = VALUES(`type`), "
                   "`description`   = VALUES(`description`), "
                   "`polyline`   = VALUES(`polyline`), "
                   "`summary_polyline`   = VALUES(`summary_polyline`), "
                   "total_photo_count   = VALUES(total_photo_count) ;",
                   (data["id"], data["athlete"]["id"], data["upload_id"], data["external_id"], data["start_date_local"],
                    data["name"], data["distance"], data["moving_time"], data["elapsed_time"],
                    data["total_elevation_gain"], data["type"], text, data["map"]["polyline"],
                    data["map"]["summary_polyline"], data["total_photo_count"])
                   )
    return data


def download_single_activity_from_strava(activity_id):
    token = auth.get_token()
    headers = {"Authorization": "Bearer "+str(token)}
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database, collation="utf8mb4_general_ci")
    cursor = db.cursor()
    d = update_activity(activity_id, cursor, headers)

    if d["total_photo_count"] > 0:
        update_photos(activity_id, cursor, headers)

    db.commit()
    db.disconnect()


def download_activities_from_strava():
    token = auth.get_token()
    headers = {"Authorization": "Bearer "+str(token)}
    for i in range(1, Credentials.activities_pages_count + 1):
        r = requests.get("https://www.strava.com/api/v3/athlete/activities?page=" + str(i) + "&before=" +
                         str(Credentials.activities_before) + "&after=" +
                         str(Credentials.activities_after) + "&per_page=" +
                         str(Credentials.activities_per_page), headers=headers)
        if r.ok:
            data = r.json()
            if len(data) == 0:
                print("No activity, end")
                break

            db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                               database=Credentials.database, collation="utf8mb4_general_ci")
            cursor = db.cursor()

            for d in data:
                # TODO: some safety checks... not necessary at this stage, but for future
                # Only store Public activities
                if d["visibility"] == "everyone":
                    update_activity(d["id"], cursor, headers)
                    if d["total_photo_count"] > 0:
                        update_photos(d["id"], cursor, headers)

            db.commit()
            db.disconnect()
