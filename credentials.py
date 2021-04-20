# For better security you should use different way of storing these secret information !!!

class Credentials:
    web_url = ""
    client_id = 0  # Your Strava API Applicationm ID - https://www.strava.com/settings/api
    client_secret = ""  # Your Strava API

    user_id = 0  # hardcoded id of single user whose data you want to read
    activities_before = 0  # hardcoded timestamp for limit displayed activities
    activities_after = 0  # hardcoded timestamp for limit displayed activities
    # DB
    host = "localhost"
    user = ""
    passwd = ""
    database = ""
