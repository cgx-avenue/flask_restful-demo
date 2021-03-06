import resources,models
from flask import Flask
from flask_restful import Api
from db import db
from flask_jwt_extended import JWTManager

app = Flask(__name__)
db.init_app(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_SECRET_KEY']='jwt-secret-string'
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']



jwt=JWTManager(app)
@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')
api.add_resource(resources.CurrentUser,'/currentuser')

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header,jwt_data):
    identity=jwt_data["sub"]
    user= models.UserModel.find_by_id(identity)
    return user




if __name__ == '__main__':

    app.run(debug=True)
