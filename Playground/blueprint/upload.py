from flask import Blueprint, render_template, session

upload = Blueprint('upload', __name__)

@upload.route('/upload')
def upload_page():
    return render_template('upload.html')

