from flask_cors import CORS
from flask import Flask
from home.views import home

app = Flask(__name__)
CORS(app)
app.register_blueprint(home)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10002)
