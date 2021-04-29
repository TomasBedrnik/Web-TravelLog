from flask import Flask
from flask import Response
from flask import request
from flask import abort
from flask import redirect
from flask import render_template
from flask import jsonify
import requests
from credentials import Credentials
import mysql.connector as mysql
from app import auth
from app import read
from datetime import datetime

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return render_template("index.html")

    @app.route('/map')
    def show_map():
        return render_template("mapycz.html", content=read.read_activities(), polylines=read.read_activities_map())

    @app.route('/mapycz')
    def show_mapycz():
        return render_template("mapycz.html", content=read.read_activities(), polylines=read.read_activities_map())

    @app.route('/activity/<int:activity_id>', methods=['GET', 'POST'])
    def show_activity(activity_id):
        if request.method == 'POST':
            print("YES")
        return render_template("activity.html", content=read.read_activity(activity_id),
                               polylines=read.read_activity_map(activity_id))

    # TODO: Delete this when alpha development stage finished
    @app.route('/refresh')
    def refresh():
        auth.get_token()
        return Response(
            "Refreshed"
        )

    # TODO: Delete this when alpha development stage finished
    @app.route('/download_single_activity_from_strava/<int:activity_id>')
    def download_single(activity_id):
        read.download_single_activity_from_strava(activity_id)
        return Response(
            "done"
        )

    # TODO: Delete this when alpha development stage finished
    @app.route('/delete_activity/<int:activity_id>')
    def delete_activity(activity_id):
        read.delete_activity(activity_id)
        return Response(
            "done"
        )

    # TODO: somehow just allow to run this only once - or only from shell to prevent bots to trigger it
    @app.route('/download_activities_from_strava')
    def download():
        read.download_activities_from_strava()
        return Response(
            "done"
        )

    @app.route('/webhook', methods=['GET', 'POST'])
    def webhook():
        if request.method == 'GET':
            # mode = request.args.get('hub.mode')
            challenge = ""
            if "hub.challenge" in request.args.keys():
                challenge = request.args.get('hub.challenge')
            # verify_token = request.args.get('hub.verify_token ')
            data = {
                "hub.challenge": challenge
                }
            return jsonify(data), 200
        elif request.method == 'POST':
            request_data = request.get_json()
            db = mysql.connect(host=Credentials.host, user=Credentials.user, passwd=Credentials.passwd,
                               database=Credentials.database)
            cursor = db.cursor()
            cursor.execute("INSERT INTO log (`date`, `text`) "
                           "VALUES (%s, %s); ", (datetime.now(), str(request_data)))
            db.commit()
            db.disconnect()
            if "aspect_type" in request_data.keys() and "object_type" in request_data.keys() and \
                    "object_id" in request_data.keys():
                if request_data["object_type"] == 'activity':
                    if request_data["aspect_type"] == 'create' or request_data["aspect_type"] == 'update':
                        read.download_single_activity_from_strava(request_data["object_id"])
                    elif request_data["aspect_type"] == 'delete':
                        read.delete_activity(request_data["object_id"])

            return "", 200

    @app.route('/authorize')
    def authorize():
        code = request.args.get('code')
        # state = request.args.get('state')
        # scope = request.args.get('scope')
        if code is None:
            # redirect to Strava authorize Page:
            return redirect("https://www.strava.com/oauth/authorize?client_id=" + str(Credentials.client_id) +
                            "&redirect_uri=" + str(Credentials.web_url) +
                            "/authorize&response_type=code&scope=activity:read")
        else:
            if auth.authorize(code):
                return Response(
                    "OK, user authorized"
                )
            else:
                abort(500, description="Something is wrong...")

    return app
