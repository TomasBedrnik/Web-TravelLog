import requests
from credentials import Credentials
import mysql.connector as mysql
from app import auth


def read_activities():
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database)
    cursor = db.cursor()
    # cursor.execute("SELECT * FROM activities")
    cursor.execute("SELECT a.id, `user_id`, `upload_id`, `external_id`, `start_date_local`, `name`, `distance`, "
                   "`moving_time`, `elapsed_time`, `total_elevation_gain`, `type`, `description`, `total_photo_count`, "
                   "GROUP_CONCAT(p.id), GROUP_CONCAT(p.url_small), GROUP_CONCAT(p.url_big), GROUP_CONCAT(p.caption) "
                   "FROM activities as a "
                   "LEFT JOIN photos as p ON a.id = p.activity_id group by a.id order by a.id desc")
    data = cursor.fetchall()
    db.commit()
    db.disconnect()
    return data


def read_activities_map():
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database)
    cursor = db.cursor()
    # cursor.execute("SELECT * FROM activities")
    cursor.execute("SELECT polyline FROM activities")
    data = cursor.fetchall()
    list_polyline = []
    for d in data:
        list_polyline.append(d[0])
    db.commit()
    db.disconnect()
    return list_polyline


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
                       database=Credentials.database)
    cursor = db.cursor()
    cursor.execute("DELETE FROM activities WHERE id='%s'; ", (activity_id,))
    cursor.execute("DELETE FROM photos WHERE activity_id='%s'; ", (activity_id,))
    db.commit()
    db.disconnect()


def update_activity(user_id, cursor, headers):
    r = requests.get("https://www.strava.com/api/v3/activities/" + str(user_id), headers=headers)
    if r.ok:
        data = r.json()
        # print(d["name"] + ": ")
        # print(data2["description"])
        # print(";")
    if "summary_polyline" not in data["map"].keys():
        print("Není tady")
        print(data["id"])
        return
    # print(d["name"])
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
                    data["total_elevation_gain"], data["type"], data["description"], data["map"]["polyline"],
                    data["map"]["summary_polyline"], data["total_photo_count"])
                   )
    return data


def download_single_activity_from_strava(activity_id):
    token = auth.get_token()
    headers = {"Authorization": "Bearer "+str(token)}
    db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                       database=Credentials.database)
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
        print("Page: "+str(i))
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
                               database=Credentials.database)
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


# read_activities()
