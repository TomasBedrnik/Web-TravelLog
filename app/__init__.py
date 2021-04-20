from flask import Flask
from flask import Response
from flask import request
from flask import abort
from flask import redirect
from flask import render_template
import requests
from credentials import Credentials
import mysql.connector as mysql
from app import auth
from app import read


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return render_template("index.html")

    @app.route('/map')
    def map():
        return render_template("map.html", content=read.read_activities(), polylines=read.read_activities_map())

    # TODO: Delete this when alpha development stage finished
    @app.route('/refresh')
    def refresh():
        auth.get_token()
        return Response(
            "Refreshed"
        )

    # TODO: somehow just allow to run this only once - or only from shell to prevent bots to trigger it
    @app.route('/download_activities_from_strava')
    def download():
        read.download_activities_from_strava()
        return Response(
            "done"
        )

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
