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


def download_activities_from_strava():
    token = auth.get_token()
    headers = {"Authorization": "Bearer "+str(token)}
    r = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers)
    if r.ok:
        data = r.json()
        if len(data) > 0:

            db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                               database=Credentials.database)
            cursor = db.cursor()

            for d in data:
                # TODO: some safety checks... not necessary at this stage, but for future
                # Only store Public activities
                if d["visibility"] == "everyone":
                    # Get Description + photos
                    r2 = requests.get("https://www.strava.com/api/v3/activities/"+str(d["id"]), headers=headers)
                    if r2.ok:
                        data2 = r2.json()
                        # print(d["name"] + ": ")
                        # print(data2["description"])
                        # print(";")

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
                                   (d["id"], d["athlete"]["id"], d["upload_id"], d["external_id"], d["start_date_local"],
                                    d["name"], d["distance"], d["moving_time"], d["elapsed_time"],
                                    d["total_elevation_gain"], d["type"], data2["description"], data2["map"]["polyline"],
                                    data2["map"]["summary_polyline"], d["total_photo_count"])
                                   )

                    # photos

                    if d["total_photo_count"] > 0:
                        r3 = requests.get("https://www.strava.com/api/v3/activities/" + str(d["id"]) +
                                          "/photos?photo_sources=true&size=200", headers=headers)
                        r4 = requests.get("https://www.strava.com/api/v3/activities/" + str(d["id"]) +
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

            db.commit()
            db.disconnect()


# read_activities()
