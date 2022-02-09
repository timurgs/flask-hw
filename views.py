from flask import jsonify, request
from flask.views import MethodView
from flask_login import login_required, login_user, current_user

import hashlib
from app import app
from validator import validate
from schema import ADV_CREATE_EDIT, USER_CREATE
from models import Advertisement, User
from app import db
from config import SALT


class AdvertisementView(MethodView):

    def get(self, adv_id):
        adv = Advertisement.by_id(adv_id)
        return jsonify(adv.to_dict())

    @login_required
    @validate('json', ADV_CREATE_EDIT)
    def post(self):
        user_id = {'user_id': current_user.id}
        adv = Advertisement(**user_id, **request.json)
        adv.add()
        return jsonify(adv.to_dict())

    @login_required
    def delete(self, adv_id):
        adv = Advertisement.by_id(adv_id)
        if adv.user_id == current_user.id:
            Advertisement.remove(adv)
            return jsonify(adv.to_dict())
        else:
            return jsonify({'status': 403,
                            "message": "You do not have permission to perform this action"})

    @login_required
    @validate('json', ADV_CREATE_EDIT)
    def patch(self, adv_id):
        adv = Advertisement.by_id(adv_id)
        if adv.user_id == current_user.id:
            Advertisement.query.filter_by(id=adv_id).update({**request.json})
            db.session.commit()
            return jsonify(adv.to_dict())
        else:
            return jsonify({'status': 403,
                            "message": "You do not have permission to perform this action"})


class UserView(MethodView):

    def get(self, user_id):
        user = User.by_id(user_id)
        return jsonify(user.to_dict())

    @validate('json', USER_CREATE)
    def post(self):
        user = User(**request.json)
        user.set_password(request.json['password'])
        user.add()
        return jsonify(user.to_dict())


class LoginView(MethodView):

    def post(self):
        if not current_user.is_authenticated:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            raw_password = f'{data.get("password")}{SALT}'
            password = hashlib.md5(raw_password.encode()).hexdigest()
            user = User.query.filter_by(username=username, email=email,
                                        password=password).first()
            if user:
                login_user(user)
                return jsonify({'status': 200, "message": "You are logged in"})
            else:
                return jsonify({"status": 401,
                                "message": "Username or Password Error"})
        else:
            return jsonify({"status": 200,
                            "message": "You are already logged in"})


app.add_url_rule('/advertisements/', view_func=AdvertisementView.as_view('adv_create'), methods=['POST', ])
app.add_url_rule('/advertisements/<int:adv_id>', view_func=AdvertisementView.as_view('adv_get_delete_update'),
                 methods=['GET', 'DELETE', 'PATCH', ])
app.add_url_rule('/users/', view_func=UserView.as_view('users_create'), methods=['POST', ])
app.add_url_rule('/users/<int:user_id>', view_func=UserView.as_view('users_get'), methods=['GET', ])
app.add_url_rule('/login/', view_func=LoginView.as_view('users_login'), methods=['POST', ])
