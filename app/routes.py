from flask import Blueprint, request, make_response
routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET', 'POST'])
def send_something():
    password = ''
    hashed_password = 'epic fail'
    response = {}
    if request.method == 'GET':
        password = 'iliketurtles'

    elif request.method == 'POST' and request.is_json():
        req = request.get_json()
        hashed_password = req['password']
    else:
        return make_response(400)

    try:
        hashed_password = argon2.hash(password)
    except Exception as e:
        hashed_password += '\n' + str(e)
    response = {
        'name': 'fred',
        'numbers': [1, 2, 3],
        'password': hashed_password
    }
    return jsonify(response)
