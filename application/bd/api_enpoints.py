import unirest as unirest

from application.opt.model import Recipe

__author__ = 'korolm'

breakfast = 'breakfast'
lunch = 'lunch'
dinner = 'dinner'
snack = 'snack'
recipes = []




def add_recipe(calories, carbs, fat, protein, stages, name):
    recipe = Recipe(calories, carbs, fat, protein, stages, name)
    recipes.append(recipe)


def get_recipes_by_query(query, stages):
    api_id = "fe68c196"
    api_key = "f912c3f7853eaf8d8dce9b4e36dcab17"
    endpoint = "https://edamam-recipe-search-and-diet-v1.p.mashape.com/search?"
    auth = "_app_id="+api_id+"&_app_key=" + api_key
    phase = "&q=" + query
    recipes = []
    for page in range(0, 5):
        page_from = page * 10
        page_to = (page + 1) * 10
        from_params = "&from=" + str(page_from) + "&to=" + str(page_to)
        api_url = endpoint + auth + phase + from_params
        response = unirest.get(api_url,
                               headers={
                                   "X-Mashape-Key": "gqH2WkciNSmshtil7Yt4VKJKj1QBp1OuoSGjsnQF0htfo5AA9k",
                                   "Accept": "application/json"
                               }
                               )
        recipes += get_recipes_from_edmam_response(response, stages)
    return recipes


def get_recipes():
    get_recipes_by_query_edamam("oatmeal", [breakfast, dinner, lunch, snack])
    get_recipes_by_query_edamam("eggs", [breakfast])
    get_recipes_by_query_edamam("chicken", [dinner, lunch])
    get_recipes_by_query_edamam("pork", [dinner, lunch])
    get_recipes_by_query_edamam("milk", [breakfast, snack])
    get_recipes_by_query_edamam("chocolate", [breakfast, snack])
    get_recipes_by_query_edamam("chocolate", [breakfast, snack])
    return recipes


def get_recipes_by_query_nutrionix(query, stages):
    endpoint = "https://nutritionix-api.p.mashape.com/v1_1/search/"
    phase = query + "?fields=item_name%2Citem_id%2Cbrand_name%2Cnf_protein%2Cnf_total_fat%2Cnf_calories%2Cnf_total_carbohydrate"
    api_url = endpoint + phase
    response = unirest.get(api_url,
                           headers={
                               "X-Mashape-Key": "gqH2WkciNSmshtil7Yt4VKJKj1QBp1OuoSGjsnQF0htfo5AA9k",
                               "Accept": "application/json"
                           }
                           )
    process_result_nutrionix(response, stages)


def process_result_nutrionix(resp, stages):
    hits = resp.body[u'hits']
    items = map(lambda hit: hit[u'fields'], hits)
    for item in items:
        add_recipe(item[u'nf_calories'], item[u'nf_total_carbohydrate'], item[u'nf_total_fat'], item[u'nf_protein'],
                   stages, item[u'item_name'] + '(' + item[u'brand_name'] + ')')


def get_recipes_by_query_edamam(query, stages):
    api_id = "fe68c196"
    api_key = "f912c3f7853eaf8d8dce9b4e36dcab17"
    endpoint = "https://edamam-recipe-search-and-diet-v1.p.mashape.com/search?"
    auth = "_app_id=fe68c196&_app_key=f912c3f7853eaf8d8dce9b4e36dcab17"
    phase = "&q=" + query
    for page in range(0, 10):
        page_from = page * 10
        page_to = (page + 1) * 10
        fromParams = "&from=" + str(page_from) + "&to=" + str(page_to)
        api_url = endpoint + auth + phase + fromParams
        response = unirest.get(api_url,
                               headers={
                                   "X-Mashape-Key": "gqH2WkciNSmshtil7Yt4VKJKj1QBp1OuoSGjsnQF0htfo5AA9k",
                                   "Accept": "application/json"
                               }
                               )
        # process_result_edamam(response, stages)


def get_recipes_from_edmam_response(resp, stages):
    hits = resp.body[u'hits']
    recipe_list = map(lambda hit: hit[u'recipe'], hits)
    for rec in recipe_list:
        rec[u'stages'] = stages
    return recipe_list


def process_result_edamam(resp, stages):
    hits = resp.body[u'hits']
    items = map(lambda hit: hit[u'recipe'], hits)
    for item in items:
        calories = item[u'calories']
        totalNutrients = item[u'totalNutrients']
        carbs = 0
        fat = 0
        protein = 0
        if u'CHOCDF' in totalNutrients:
            carbs = totalNutrients[u'CHOCDF'][u'quantity']
        else:
            continue
        if u'FAT' in totalNutrients:
            fat = totalNutrients[u'FAT'][u'quantity']
        else:
            continue
        if u'PROCNT' in totalNutrients:
            protein = totalNutrients[u'PROCNT'][u'quantity']
        else:
            continue
        name = item[u'label']
        add_recipe(calories, carbs, fat, protein, stages, name)
