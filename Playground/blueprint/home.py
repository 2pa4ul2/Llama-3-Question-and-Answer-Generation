from flask import Blueprint, render_template, session

home = Blueprint('home', __name__)

@home.route('/home')
def home_page():
    return render_template('home.html')

