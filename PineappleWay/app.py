from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = os.getenv("SECRET_KEY")

from routes.main import *
from routes.auth import *
from routes.booking import *
from routes.admin import *

if __name__ == "__main__":
    app.run(debug=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"),500