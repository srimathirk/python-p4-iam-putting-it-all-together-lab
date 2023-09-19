#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        image_url = request.get_json().get('image_url')
        bio = request.get_json().get('bio')
        if not username or not password:
            return {'error': 'invalid username'}, 422
        
        new_user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        new_user.password_hash = password

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        response_json = {
            'id': new_user.id,
            'username': new_user.username,
            'bio':new_user.bio,
            'image_url':new_user.image_url
        }
        return response_json, 201

    
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            response_json = {
                'id': user.id,
                'username': user.username,
            }
            return response_json, 200
        
        return {}, 401


class Login(Resource):
    def post(self):
        
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()
        
        if user:
            password = request.get_json()['password']


            # users pwd is set by calling user.pawd = "new_pwd"
            # instead of pwd = user.pwd , here we authenticate by using bcrypt checking pwd = stored pwd hash
            if user.authenticate(password):
            
                session['user_id'] = user.id
                return {
                    'id':user.id,
                    'username':user.username,
                    'image_url':user.image_url,
                    'bio':user.bio
                }, 201

            return {}, 200
        return {},401

class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            
            return {}, 204
        else:
            return {}, 401

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            recipe_list = []
            for recipe in Recipe.query.all():
                recipe_dict = {
                    'title': recipe.title,
                    'instructions':recipe.instructions,
                    'minutes_to_complete':recipe.minutes_to_complete,
                    'user_id': session['user_id']
                }
                recipe_list.append(recipe_dict)
            return recipe_list,200
        return {},401

    def post(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            data = request.get_json()
            # title=data['title']
            # instructions=data['instructions']
            # minutes_to_complete=data['minutes_to_complete']
            # user_id = session['user_id']
            # recipes = Recipe.query.filter(Recipe.user_id == user_id).all()
            # for recipe in recipes:
            #     user = User.query.filter(User.id == user_id).first()
            try:
                new_recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data['minutes_to_complete'],
                    user_id = session['user_id']
                )

                db.session.add(new_recipe)
                db.session.commit()
            except IntegrityError:
                return {},422

            return(
                {
                    'title': new_recipe.title,
                    'instructions':new_recipe.instructions,
                    'minutes_to_complete':new_recipe.minutes_to_complete,
                    'user_id':new_recipe.user_id
                }
            ),201
        return {}, 401
    

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
