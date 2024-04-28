# create flask app 

from flask import Flask
def create_app(): 
    app = Flask(__name__)
    app.config['SECRET KEY'] = '04468aff0e3acbb6c65b62e4150e227d'
    return app