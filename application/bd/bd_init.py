from pymongo import MongoClient

from application.bd.api_enpoints import get_recipes_by_query

client = MongoClient()

db = client.oatmeal

recipes = db.recipes
breakfast = 'breakfast'
lunch = 'lunch'
dinner = 'dinner'
snack = 'snack'

def get_recipes():
    return list(recipes.find({}))


if __name__ == "__main__":
    # delete all data
    recipes.delete_many({})

    # query
    query_result = []
    query_result += get_recipes_by_query("oatmeal", [breakfast])
    query_result += get_recipes_by_query("chicken", [lunch, dinner])
    query_result += get_recipes_by_query("meat", [lunch, dinner])
    query_result += get_recipes_by_query("milk", [breakfast, snack])
    query_result += get_recipes_by_query("chocolate", [snack])
    query_result += get_recipes_by_query("pasta", [lunch])
    query_result += get_recipes_by_query("salad", [lunch, dinner])
    query_result += get_recipes_by_query("tomato", [lunch, dinner])
    query_result += get_recipes_by_query("cherry", [snack])

    recipes.insert_many(query_result)
