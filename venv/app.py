from flask import Flask, jsonify, request, Response
from BookModel import *
from settings import *
from UserModel import User
from functools import wraps
import json
import jwt
import datetime


books = Book.get_all_books()

DEFAULT_PAGE_LIMIT = 3

app.config['SECRET_KEY'] = 'meow'

def valid_book_object(bookObject):
	if ("name" in bookObject and "price" in bookObject and "isbn" in bookObject):
		return True
	else:
		return False


def valid_put_request_data(request_data):
    if("name" in request_data and "price" in request_data):
        return True
    else:
        return False


def token_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		token = request.args.get('token')
		try:
			jwt.decode(token, app.config['SECRET_KEY'])
			return f(*args, **kwargs)
		except:
			return jsonify({'error': 'Need a valid token to view this page'}), 401
	return wrapper

@app.route('/login', methods=['POST'])
def get_token():
	request_data = request.get_json()
	username = str(request_data['username'])
	password = str(request_data['password'])

	match = User.username_password_match(username, password)

	if match:
		expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
		token = jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
		return token
	else:
		return Response('', 401, mimetype='application/json')


@app.route('/books')
def get_books():
	return jsonify({'books': Book.get_all_books()})


@app.route('/books/<int:isbn>')
def get_book_by_isbn(isbn):
	return_value = Book.get_book(isbn)
	return jsonify(return_value)


@app.route('/books', methods=['POST'])
@token_required
def add_book():
	request_data = request.get_json()
	if (valid_book_object(request_data)):
		Book.add_book(request_data['name'], request_data['price'], request_data['isbn'])
		response = Response("", 201, mimetype='application/json')
		response.headers['Location'] = "/books/" + str(request_data['isbn'])
		return response
	else:
		invalidBookObjectErrorMsg = {
			"error": "Invalid book object passed in request",
			"helpString": "Data passed in similar to this {'name: 'bookname', 'price': 7.99, 'isbn': 23423465}"
		}
		response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
		return response


@app.route('/books/<int:isbn>', methods=['PUT'])
@token_required
def replace_book(isbn):
	request_data = request.get_json()
	if (not valid_put_request_data(request_data)):
		invalidBookObjectErrorMsg = {
			"error": "Invalid book object passed in request",
			"helpString": "Data passed in similar to this {'name: 'bookname', 'price': 7.99, 'isbn': 23423465}"
		}
		response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
		return response
	Book.replace_book(isbn, request_data['name'], request_data['price'])
	response = Response("", status=204)
	return response


@app.route('/books/<int:isbn>', methods=['PATCH'])
@token_required
def update_book(isbn):
	request_data = request.get_json()

	if ("name" in request_data):
		Book.update_book_name(isbn, request_data['name'])
	if ("price" in request_data):
		Book.update_book_price(isbn, request_data['price'])

	response = Response("", status=204)
	response.headers['Location'] = "/books/" + str(isbn)

	return response


@app.route('/books/<int:isbn>', methods=['DELETE'])
@token_required
def delete_book(isbn):
	if (Book.delete_book(isbn)):
		response = Response("", status=204)
		return response

	invalidBookObjectErrorMsg = {
		"error": "Book with the ISBN number was not found so therefore unable to Delete"
	}

	response = Response(json.dumps(invalidBookObjectErrorMsg), status=404, mimetype='application/json')
	return response


app.debug = True
app.run(port=5000)