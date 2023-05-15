#!/usr/bin/env python3
# 📚 Review With Students:
# Set up:
    # cd into server and run the following in Terminal:
        # export FLASK_APP=app.py
        # export FLASK_RUN_PORT=5000
        # flask db init
        # flask db revision --autogenerate -m'Create tables' 
        # flask db upgrade 
        # python seed.py
# Running React Together 
     # In Terminal, run:
        # `honcho start -f Procfile.dev`

from flask import request, make_response, session, jsonify, abort, render_template
from flask_restful import Resource
from werkzeug.exceptions import NotFound, Unauthorized
from flask_cors import CORS

from config import app, db, api

# 1.✅ Import Bcrypt form flask_bcrypt
    #1.1 Create config.py and inport Bcrypt there
    #1.2 Move other imports and configs to config py
    #1.3 Invoke Bcrypt and pass it app on config.py
    #1.4 Do required import from config.py to app.py and models.py



# 2.✅ Navigate to "models.py"
    # Continue on Step 3


CORS(app) 

from models import Production, CastMember, User

# adding authorization check for backend routes
# before_request decorator invokes its method before
# each incoming request get routed to its view
# endpoint names are derived from Resource class names below (but can also be explicity
# given as arguments to api.add_resource())
@app.before_request
def check_if_logged_in():
    # these are routes you DON'T want to protect! If a user had to be logged in
    # in order to send a /login request... you see the problem!
    open_access_list = [
        'productions',
        'signup',
        'login',
        'logout',
        'authorizedsession',
        'index',
        'static'
    ]

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
        raise Unauthorized
        # return {'error': '401 Unauthorized'}, 401

@app.route('/')
@app.route('/<int:id>')
def index(id=0):
    return render_template("index.html")

class Productions(Resource):
    def get(self):
        production_list = [p.to_dict() for p in Production.query.all()]
        response = make_response(
            production_list,
            200,
        )

        return response

    def post(self):
        form_json = request.get_json()
        try:
            new_production = Production(
                title=form_json['title'],
                genre=form_json['genre'],
                budget=int(form_json['budget']),
                image=form_json['image'],
                director=form_json['director'],
                description=form_json['description']
            )
        except ValueError as e:
            abort(422,e.args[0])

        db.session.add(new_production)
        db.session.commit()

        response_dict = new_production.to_dict()

        response = make_response(
            response_dict,
            201,
        )
        return response
api.add_resource(Productions, '/productions')


class ProductionByID(Resource):
    def get(self,id):
        production = Production.query.filter_by(id=id).first()
        if not production:
            raise NotFound
        production_dict = production.to_dict()
        response = make_response(
            production_dict,
            200
        )
        
        return response

    def patch(self, id):
        production = Production.query.filter_by(id=id).first()
        if not production:
            raise NotFound

        for attr in request.form:
            setattr(production, attr, request.form[attr])

        production.ongoing = bool(request.form['ongoing'])
        production.budget = int(request.form['budget'])

        db.session.add(production)
        db.session.commit()

        production_dict = production.to_dict()
        
        response = make_response(
            production_dict,
            200
        )
        return response

    def delete(self, id):
        production = Production.query.filter_by(id=id).first()
        if not production:
            raise NotFound
        db.session.delete(production)
        db.session.commit()

        response = make_response('', 204)
        
        return response
api.add_resource(ProductionByID, '/productions/<int:id>')

# 10.✅ Create a Signup route
    #10.1 Use add_resource to add a new endpoint '/signup' 
    #10.2 The signup route should have a post method
        #10.2.1 Get the values from the request body with get_json
        #10.2.2 Create a new user, however only pass in the name, email and admin values
        #10.2.3 Call the password_hash method on the new user and set it to the password from the request
        #10.2.4 Add and commit
        #10.2.5 Add the user id to session under the key of user_id
        #10.2.6 send the new user back to the client with a status of 201
    #10.3 Test out your route with the client or Postman
class Signup(Resource):
    def post(self):
        form_json = request.get_json()
        new_user = User(name=form_json['name'], email=form_json['email'])
        #Hashes our password and saves it to _password_hash
        new_user.password_hash = form_json['password']

        db.session.add(new_user)
        db.session.commit()
        # Add new users id to session
        session['user_id'] = new_user.id
        response = make_response(
            new_user.to_dict(),
            201
        )
        return response
api.add_resource(Signup, '/signup', endpoint='signup')

# User.query.order_by(User.id.desc()).first()._password_hash

# 11.✅ Create a Login route
    #11.1 use add add_resource to add the login endpoint
    #11.2 Create a post method
        #11.2.1 Query the user from the DB with the name provided in the request
        #11.2.2 Set the user's id to sessions under the user_id key
        #11.2.3 Create a response to the client with the user's data

#12 Head to client/components/authenticate 
class Login(Resource):
    def post(self):
            user = User.query.filter_by(name=request.get_json()['name']).first()
            # add password authentication to user
            if user and user.authenticate(request.get_json()['password']):
                session['user_id'] = user.id
                response = make_response(
                    user.to_dict(),
                    200
                )
                return response
            else:
                raise Unauthorized
                # abort(401, "Incorrect Username or Password")

api.add_resource(Login, '/login')

# 13.✅ Create a route that checks to see if the User is currently in sessions
    # 13.1 Use add_resource to add an authorized endpoint
    # 13.2 Create a Get method
        #13.2.1 Check to see if the user_id is in session
        #13.2.2 If found query the user and send it to the client
        #13.2.3 If not found return a 401 Unauthorized error
class AuthorizedSession(Resource):
    def get(self):
        try:
            user = User.query.filter_by(id=session['user_id']).first()
            response = make_response(
                user.to_dict(),
                200
            )
            return response
        except:
            # abort(401, "Unauthorized")
            raise Unauthorized

api.add_resource(AuthorizedSession, '/authorized')

# 14.✅ Create a Logout route
    #14.1 Use add_resource to add a logout endpoint
    #14.2 Create a delete method
        # 14.2.1 Set the user_id in sessions to None
        # 14.2.1 Create a response with no content and a 204
    #14.3 Test out your route with the client or Postman

class Logout(Resource):
    def delete(self):
        session['user_id'] = None 
        response = make_response('',204)
        return response
api.add_resource(Logout, '/logout')

# 14.✅ Navigate to client navigation

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: Sorry the resource you are looking for does not exist",
        404
    )

    return response

@app.errorhandler(Unauthorized)
def handle_unauthorized(e):
    response = make_response(
        {"error": "Unauthorized: you must be logged in to make that request."},
        401
    )
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
