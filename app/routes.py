from io import BytesIO

from app import app
from app.models import User, Data
from functools import wraps
from flask import request, jsonify, make_response, send_file
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from app import db
import datetime


@app.route('/')
@app.route('/index')
def index():
    return "Hi, Please login using /login!"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing from the request!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid, please refresh the token!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': "The user does not exist in the system!"}), 401

    user_data = {'public_id': user.public_id, 'username': user.username, 'password': user.password,
                 'email': user.email}

    return jsonify({'user': user_data})


@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Not allowed to perform that function!'}), 401

    data = request.get_json()
    admin = (data["admin"].lower() == "true")
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password,
                    email=data["email"], admin=admin)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@app.route('/download/<public_id>')
@token_required
def get_data(current_user, public_id):
    data = Data.query.filter_by(public_id=public_id).first()
    if not data:
        return jsonify({'message': "The file does not exist in the system!"}), 401
    return send_file(BytesIO(data.data), attachment_filename=data.public_id, as_attachment=True)


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
                           , app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
