import json
import copy

from flask import Response
from flask import request
from bson import json_util
from bson.objectid import ObjectId

from application import app
from application import mongo
from application import data
from application.opt.oatmeal import generate_ration


@app.route('/')
@app.route('/index')
def index():
    return 'Home'


@app.route('/recipes', methods=['GET'])
def recipes():
    return Response(json_util.dumps(get_all_recipes_list()), mimetype='application/json')


@app.route('/recipes/<recipe_id>', methods=['GET'])
def recipes_by_id(recipe_id):
    recipe_id = recipe_id
    recipes_collection = get_recipes()
    recipe_object = list(recipes_collection.find({'_id': ObjectId(recipe_id)}))
    return Response(json_util.dumps(recipe_object), mimetype='application/json')


@app.route('/ration', methods=['GET'])
def ration():
    calories = int(request.args.get("calories", 2300))
    carbs = int(request.args.get("carbs", 200))
    fat = int(request.args.get("fat", 80))
    protein = int(request.args.get("protein", 250))
    print [calories, carbs, fat, protein]
    best_ration = generate_ration([calories, carbs, fat, protein])
    values = {
        'meals': [],
        'replacement': []
    }
    for meal in best_ration:
        m = copy.deepcopy(meal)
        m.recipe.data = json.loads(json_util.dumps(get_recipes_by_id(m.recipe.id)[0]))
        val = json.dumps(m, default=lambda o: o.__dict__)
        values['meals'].append(json.loads(val))
    for meals_list in best_ration.top_meals:
        index_meals = []
        for meal in meals_list:
            m = copy.deepcopy(meal)
            m.recipe.data = json.loads(json_util.dumps(get_recipes_by_id(m.recipe.id)[0]))
            val = json.dumps(m, default=lambda o: o.__dict__)
            index_meals.append(json.loads(val))
        values['replacement'].append(index_meals)
    return Response(json.dumps(values), mimetype='application/json')


def get_recipes():
    client = mongo.cx
    db = client.oatmeal
    return db.recipes


def get_recipes_by_id(recipe_id):
    recipe_id = recipe_id
    recipes_collection = get_recipes()
    recipe_object = list(recipes_collection.find({'_id': ObjectId(recipe_id)}))
    return recipe_object


def get_all_recipes_list():
    if 'recipes' not in data:
        data['recipes'] = list(get_recipes().find({}))
    return data['recipes']
