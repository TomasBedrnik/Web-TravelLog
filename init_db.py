import mysql.connector as mysql

from credentials import Credentials

db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                   database=Credentials.database)

cursor = db.cursor()

# TODO: add foreign keys
# ## check if table exist... create it
cursor.execute("SHOW TABLES like 'user_credentials'")
result = cursor.fetchone()
if not result:
    cursor.execute("CREATE TABLE `user_credentials` "
                   "(`id` bigint NOT NULL PRIMARY KEY,"
                   "`refresh_token` varchar(255) NOT NULL,"
                   "`access_token` varchar(255) NOT NULL,"
                   "`expires_at` int NOT NULL)")

cursor.execute("SHOW TABLES like 'activities'")
result = cursor.fetchone()
if not result:
    cursor.execute("CREATE TABLE `activities` "
                   "(`id` bigint NOT NULL PRIMARY KEY,"
                   "`user_id` bigint NOT NULL,"
                   "`upload_id` bigint NOT NULL,"
                   "`external_id` varchar(255) NOT NULL,"
                   "`start_date_local` varchar(255) NOT NULL,"
                   "`name` varchar(255) NOT NULL,"
                   "`distance` FLOAT NOT NULL,"
                   "`moving_time` FLOAT NOT NULL,"
                   "`elapsed_time` FLOAT NOT NULL,"
                   "`total_elevation_gain` FLOAT NOT NULL,"
                   "`type` varchar(50) NOT NULL,"
                   "`description` text ,"
                   "`polyline` mediumtext ,"
                   "`summary_polyline` text ,"
                   "`total_photo_count` int NOT NULL)")

cursor.execute("SHOW TABLES like 'photos'")
result = cursor.fetchone()
if not result:
    cursor.execute("CREATE TABLE `photos` "
                   "(`id` varchar(255) NOT NULL PRIMARY KEY,"                   
                   "`photo_order` bigint NOT NULL AUTO_INCREMENT,"
                   "`activity_id` bigint NOT NULL,"
                   "`caption` text NOT NULL,"
                   "`url_small` varchar(255) NOT NULL,"
                   "`url_big` varchar(255) NOT NULL)")

cursor.execute("SHOW TABLES like 'log'")
result = cursor.fetchone()
if not result:
    cursor.execute("CREATE TABLE `log` "
                   "(`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                   "`date` varchar(255),"
                   "`text` text)")


cursor.execute("SHOW TABLES like 'comments'")
result = cursor.fetchone()
if not result:
    cursor.execute("CREATE TABLE `comments` "
                   "(`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                   "`activity_id` bigint NOT NULL,"
                   "`date` datetime,"
                   "`name` varchar(255),"
                   "`text` text)")
db.commit()
db.disconnect()

