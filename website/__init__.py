# create flask app 

from flask import Flask
def create_app(): 
    app = Flask(__name__)
    app.config['SECRET KEY'] = '04468aff0e3acbb6c65b62e4150e227d'
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix= '/')
    app.register_blueprint(auth, url_prefix = '/')
    return app