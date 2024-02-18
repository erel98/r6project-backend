from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, JWTManager
from database import db
from database_models import User
from datetime import timedelta
from sqlalchemy import asc, desc


class DefaultResponse:
    def __init__(self, data=None, error=''):
        self.error = error
        self.data = data
        self.body = {'error': error,
                     'data': data}


access_expires = timedelta(hours=5)
refresh_expires = timedelta(weeks=1)


def create_app():
    application = Flask(__name__)
    application.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://newuser:password@localhost/postgres'
    application.config['JWT_SECRET_KEY'] = 'MonsterTulparT5V19.1'
    application.config['JWT_ACCESS_TOKEN_EXPIRES'] = access_expires
    application.config['JWT_REFRESH_TOKEN_EXPIRES'] = refresh_expires
    application.config['DEFAULT_USER'] = 'admin'
    db.init_app(application)
    return application


app = create_app()
jwt = JWTManager(app)
bcrypt = Bcrypt(app)


@jwt.expired_token_loader
def handle_expired_token_callback(header, data):
    response = DefaultResponse(error='Token has expired')
    return jsonify(response.body), 401


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()

    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    response = DefaultResponse(data={'access_token': access_token, 'refresh_token': refresh_token})

    return jsonify(response.body)


@app.route('/register', methods=['POST'])
def register_user():
    post_data = request.get_json()

    name = post_data.get('name')
    username = post_data.get('username')
    email = post_data.get('email')
    encrypted_password = bcrypt.generate_password_hash(post_data.get('password'))
    # Check if the email exists:
    result = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if result:
        response = DefaultResponse(
            error='This email already exists. Please reset your password if you forgot your password.')
        return jsonify(response.body), 409
    # Check if the username exists:
    result = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    if result:
        response = DefaultResponse(
            error='This username is already in use. Please choose a different username.')
        return jsonify(response.body), 409
    # Create new user
    user = User(
        name=name,
        username=username,
        email=email,
        password=encrypted_password.decode('utf-8'),
    )

    db.session.add(user)
    db.session.commit()

    response = DefaultResponse(data={'user': user.serialize()})
    return jsonify(response.body)


@app.route('/login', methods=['POST'])
def login():
    post_data = request.get_json()
    email = post_data.get('email')
    password = post_data.get('password')

    result = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

    if not result or not bcrypt.check_password_hash(result.password, password):
        response = DefaultResponse(error='Invalid credentials')
        return jsonify(response.body), 401

    access_token = create_access_token(identity=result.id)
    refresh_token = create_refresh_token(identity=result.id)
    response = DefaultResponse(data={'access_token': access_token, 'refresh_token': refresh_token})

    return jsonify(response.body)


@app.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    id = get_jwt_identity()

    result = db.session.execute(db.select(User).filter_by(id=id)).scalar_one_or_none()

    response = DefaultResponse(data={'user': result.serialize()})
    return jsonify(response.body)


@app.route('/players', methods=['GET'])
@jwt_required()
def get_players():
    # Filter arguments
    min_rank = request.args.get('min_rank')
    max_rank = request.args.get('max_rank')
    has_mic = request.args.get('has_mic')
    platform = request.args.get('platform')
    # Sort arguments
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', default='asc')

    query = db.select(User)

    if min_rank is not None:
        query = query.filter(User.rank >= min_rank)
    if max_rank is not None:
        query = query.filter(User.rank <= max_rank)
    if has_mic is not None:
        query = query.filter(User.hasMic == has_mic)
    if platform:
        query = query.filter(User.platform == platform)

    if sort_by:
        if sort_order == 'desc':
            query = query.order_by(desc(sort_by))
        else:
            query = query.order_by(asc(sort_by))

    # Execute the query
    result = db.session.execute(query).scalars().all()

    serialized_result = []
    for user in result:
        serialized_result.append(user.serialize())

    response = DefaultResponse(data={'players': serialized_result})

    return jsonify(response.body)


if __name__ == '__main__':
    app.run()

