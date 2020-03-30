from flask import Flask, jsonify, request, Response
import json


app = Flask(__name__)

books = [
	{
		'name': 'Green Eggs and Ham',
		'price': 7.99,
		'isbn': 937459359
	},
	{
		'name': "The Cat In The Hat",
		'price': 6.99,
		'isbn': 4098358439
	}

]

def valid_book_object(bookObject):
	if ("name" in bookObject and "price" in bookObject and "isbn" in bookObject):
		return True
	else:
		return False


# decorator binds a function to a URL
@app.route('/books')
def display_books():
	return jsonify({'books': books})


@app.route('/books/<int:isbn>')
def get_book_by_isbn(isbn):
	return_value = {}
	for book in books:
		if book["isbn"] == isbn:
			return_value = {
				'name': book["name"],
				'price':book["price"]
			}

	return jsonify(return_value)


@app.route('/books', methods=['POST'])
def add_book():
	request_data = request.get_json()
	if(valid_book_object(request_data)):
		new_book = {
			"name": request_data['name'],
			"price": request_data['price'],
			"isbn": request_data['isbn']
		}
		books.insert(0, new_book)
		response = Response("", 201, mimetype='application/json')
		response.headers['Location'] = "/books/" + str(new_book['isbn'])
		return response
	else:
		invalidBookObjectErrorMsg = {
			"error": "Invalid book object passed in request",
			"helpString": "Data passed in similar to this {'name: 'bookname', 'price': 7.99, 'isbn': 23423465}"
		}
		response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
		return response


@app.route('/books/<int:isbn>', methods=['PUT'])
def replace_book(isbn):
	request_data =  request.get_json()
	if(not valid_book_object(request_data)):
		invalidBookObjectErrorMsg = {
			"error": "Invalid book object passed in request",
			"helpString": "Data passed in similar to this {'name: 'bookname', 'price': 7.99, 'isbn': 23423465}"
		}
		response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
		return response

	new_book = {
		'name': request_data['name'],
		'price': request_data['price'],
		'isbn': isbn
	}
	i = 0
	for book in books:
		currentIsbn = book['isbn']
		if currentIsbn == isbn:
			books[i] = new_book
		i += 1
	response = Response("", status=204)
	return response


@app.route('/books/<int:isbn>', methods=['PATCH'])
def update_book(isbn):
	request_data = request.get_json()
	updated_book = {}

	if("name" in request_data):
		updated_book["name"] = request_data['name']
	if ("price" in request_data):
		updated_book["price"] = request_data['price']

	for book in books:
		if book["isbn"] == isbn:
			book.update(updated_book)
	response = Response("", status=204)
	response.headers['Location'] = "/books/" + str(isbn)

	return response


@app.route('/books/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
	counter = 0
	for book in books:
		if book['isbn'] == isbn:
			books.pop(counter)
			response = Response("", status=204)
			return response
		counter += 1

	invalidBookObjectErrorMsg = {
		"error": "Book with the ISBN number was not found so therefore unable to Delete"
	}

	response = Response(json.dumps(invalidBookObjectErrorMsg), status=404, mimetype='application/json')
	return response


app.debug = True
app.run(port=5000)