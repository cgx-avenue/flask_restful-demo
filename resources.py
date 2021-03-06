
from flask_jwt_extended.utils import get_jti
from flask_restful import Resource, reqparse
from flask_jwt_extended import (current_user,
                                create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from models import RevokedTokenModel, UserModel

parser = reqparse.RequestParser()
parser.add_argument(
    'username', help='This field cannot be blank', required=True)
parser.add_argument(
    'password', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args(strict=True)
        if UserModel.find_by_username(data['username']):
            return {'msg': 'User {} already exists'.format(data['username'])}
        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            # access_token = create_access_token(identity=data['username'])
            access_token = create_access_token(identity=new_user)
            refresh_token = create_refresh_token(identity=new_user)

            # refresh_token = create_refresh_token(identity=data['username'])
            return {
                'msg': 'user {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        except:
            return {
                'msg': 'sth went wrong'
            }, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            # access_token=create_access_token(identity=data['username'])
            # refresh_token=create_refresh_token(identity=data['username'])
            access_token = create_access_token(identity=current_user)
            refresh_token = create_refresh_token(identity=current_user)
            return {'message': 'Logged in as {}'.format(current_user.username),
                    'access_token': access_token,
                    'refresh_token': refresh_token}
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'msg': 'sth went wrong'}


class UserLogoutRefresh(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'msg': 'Refresh token has been revoked'}
        except:
            return {'message': 'sth went wrong'}


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = UserModel.find_by_id(get_jwt_identity())
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class CurrentUser(Resource):
    @jwt_required()
    def get(self):
        return {'id': current_user.id, 'username': current_user.username}


class SecretResource(Resource):
    @jwt_required()
    def get(self):
        return {
            'answer': 42
        }
