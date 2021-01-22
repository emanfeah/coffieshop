import os
import sys

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


## ROUTES
# this for get all drinks
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(token):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    try:
        body = request.get_json()
        drink = Drink(
            title=body.get('title'),
            recipe=json.dumps(body.get('recipe'))
        )

        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except:
        print(sys.exc_info())
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink_submission(token, drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)
        drink.title = body.get('title')
        drink.recipe = json.dumps(body.get('recipe'))
        drink.update()

    except:
        print(sys.exc_info())
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink.id,
        })
    except:
        abort(404)


## Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def handle_auth_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response
