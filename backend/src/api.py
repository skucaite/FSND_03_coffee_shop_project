import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def short_drinks():
    drinks_list = Drink.query.all()
    try:
        drinks = [drink.short() for drink in drinks_list]

        # if len(drinks) == 0:
        #     abort(404)

        return jsonify({
        'success': True,
        'drinks': drinks
        })
    except Exception:
        abort(404)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def long_drinks(jwt):
    drinks_list = Drink.query.all()
    try:
        drinks = [drink.long() for drink in drinks_list]

        # if len(drinks) == 0:
        #     abort(404)

        return jsonify({
        'success': True,
        'drinks': drinks
        })
    except Exception:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    # if body == None:
    #     abort(404)
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()
        drink = [new_drink.long()]
        return jsonify({
            'success': True,
            'drinks': drink
        })
    except Exception:
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    body = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        else:
            drink.title = body.get('title')
            drink.recipe = json.dumps(body.get('recipe'))

            drink.update()
            drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': drink
        })

    except Exception:
        abort(400)

# Delete drink
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
          abort(404)
        else:
          drink.delete()
          return jsonify({
            'success': True,
            'delete': id,
            })
    except Exception:
        abort(422)

# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(AuthError)
def auth_error_message(error):
    message = str(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "description": message
    }), error.status_code


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


if __name__ == '__main__':
    app.run(port=5000)
