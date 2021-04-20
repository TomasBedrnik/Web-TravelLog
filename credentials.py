# For better security you should use different way of storing these secret information !!!
# if you use this file, NEVER PUBLISH IT ON GITHUB!!!!
# USE $git update-index --skip-worktree FILENAME
class Credentials:
    web_url = "youdomain.com"
    client_id = 0  # Your Strava API Applicationm ID - https://www.strava.com/settings/api
    client_secret = "abc"  # Your Strava API

    user_id = 0  # hardcoded id of single user whose data you want to read
    activities_before = 0  # hardcoded timestamp for limit displayed activities
    activities_after = 0  # hardcoded timestamp for limit displayed activities
    # DB
    host = "localhost"
    user = "dbUser"
    passwd = "dbPasswd"
    database = "dbName"
