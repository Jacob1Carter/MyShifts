from flask import session, Blueprint, render_template, request, redirect


playerready = Blueprint("playerready", __name__)

@playerready.route("/")
def landing():
    return ""