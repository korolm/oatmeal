import heapq
import random
import time

from deap import algorithms, base, creator, tools

from application.bd.bd_init import get_recipes
from application.opt.model import Recipe
from application.opt.model import Meal

breakfast = 'breakfast'
lunch = 'lunch'
dinner = 'dinner'
snack = 'snack'

global oat_data
oat_data = {'recipes': [], 'target': [], 'priorities': [6, 1, 1, 1], 'population': 150, 'ngen': 30}
toolbox = base.Toolbox()
servings = [0.125, 0.25, 0.5, 1, 2]


def generate_stage_recipes():
    for stage in [breakfast, snack, lunch, dinner]:
        if stage not in oat_data:
            oat_data[stage] = [rec for rec in oat_data['recipes'] if rec.valid_stage(stage)]


def get_ration_nutrion(ration):
    meals = map(lambda meal: meal.get_nutrion(), ration)
    return map(sum, zip(*meals))


def generate_random_meal(stage):
    stage_recipes = oat_data[stage]
    return Meal(random.choice(stage_recipes), random.choice(servings), stage)


def generate_random_ration(individual):
    ration = individual()
    for stage in [lunch, dinner]:
        for i in range(0, 2):
            ration.append(generate_random_meal(stage))
    for stage in [breakfast, snack]:
        for i in range(0, 1):
            ration.append(generate_random_meal(stage))
    return ration


def evaluate_nutrion(individual, target):
    calories, carbs, fat, protein = get_ration_nutrion(individual)
    priorities = oat_data['priorities']
    targ = map(lambda pair: pair[0] / pair[1], zip(target, priorities))
    vals = map(lambda pair: pair[0] / pair[1], zip([calories, carbs, fat, protein], priorities))
    pairs = zip(vals, targ)
    squerror = map(lambda pair: ((pair[0] - pair[1]) ** 2) / len(target), pairs)
    return sum(squerror),


def mutate_ration(individual):
    meal = random.choice(individual)
    stage_recipes = [rec for rec in oat_data['recipes'] if rec.valid_stage(meal.stage)]
    meal.recipe = random.choice(stage_recipes)
    meal.serving = random.choice(servings)
    return individual,


def init_toolbox():
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin, top_meals=[])
    toolbox.register("generate_ration", generate_random_ration)
    toolbox.register("individual", toolbox.generate_ration, creator.Individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_ration)
    toolbox.register("select", tools.selTournament, tournsize=3)
    return toolbox


def init_recipes(selected_recipes):
    if 'recipes' in oat_data and len(oat_data['recipes']) > 0:
        return
    else:
        for recipe in selected_recipes:
            formatted = format_recipe(recipe)
            if formatted is not None:
                oat_data['recipes'].append(formatted)
        generate_stage_recipes()


def generate_ration(user_target):
    t0 = time.time()
    toolbox.register("evaluate", evaluate_nutrion, target=user_target)
    init_recipes(get_recipes())
    init_toolbox()
    print "Init recipes time:" + str(time.time() - t0)
    oat_data['target'] = user_target
    pop = toolbox.population(n=oat_data['population'])
    print "Population generated time:" + str(time.time() - t0)
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=False)
    # my_eas(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=data['ngen'], verbose=False)
    best = tools.selBest(pop, k=1)[0]
    print "Best received time:" + str(time.time() - t0)
    post_processing(best, user_target)
    print "Post process time:" + str(time.time() - t0)
    # print_ration(best)
    t1 = time.time()
    print "Population:" + str(oat_data['population'])
    print "NGEN: " + str(oat_data['ngen'])
    print "Execution time:" + str(t1 - t0)
    return best


def generate_ration_my_eas(selected_recipes, user_target):
    toolbox.register("evaluate", evaluate_nutrion, target=user_target)
    init_recipes(selected_recipes)
    for recipe in selected_recipes:
        formatted = format_recipe(recipe)
        if formatted is not None:
            oat_data['recipes'].append(formatted)

    oat_data['target'] = user_target
    pop = toolbox.population(n=oat_data['population'])
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=False)
    # my_eas(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=data['ngen'], verbose=False)
    best = tools.selBest(pop, k=1)[0]
    post_processing(best, user_target)
    # print_ration(best)
    return best


def post_processing(ration, user_target):
    for index in range(0, len(ration)):
        nutrion_without_meal = get_nutrions_without_meal(ration, index)
        nutrion_for_new_meal = get_nutrions_target_for_meal(nutrion_without_meal, user_target)
        ration.top_meals.append(find_top_meals(nutrion_for_new_meal, ration[index].stage))


def get_nutrions_without_meal(ration, index):
    y = ration[:]  # fastest way to copy
    y.pop(index)
    meals = map(lambda meal: meal.get_nutrion(), y)
    return map(sum, zip(*meals))


def get_nutrions_target_for_meal(ration_target, user_target):
    return map(lambda p: p[0] - p[1], zip(user_target, ration_target))


def find_top_meals(nutrions_target, stage):
    top = []
    stage_recipes = [rec for rec in oat_data['recipes'] if rec.valid_stage(stage)]
    for recipe in stage_recipes:
        meal = Meal(recipe, 1, stage)
        eval_rank = evaluate_nutrion([meal], nutrions_target)[0]
        if len(top) < 10:
            heapq.heappush(top, (-eval_rank, meal))
        else:
            heapq.heappushpop(top, (-eval_rank, meal))
    return map(lambda t: t[1], top)[::-1]


def heapsort(heap):
    return [heapq.heappop(heap) for _ in range(len(heap))]


def format_recipe(item):
    calories = item[u'calories']
    totalNutrients = item[u'totalNutrients']
    id = item[u'_id']
    carbs = 0
    fat = 0
    protein = 0
    if u'CHOCDF' in totalNutrients:
        carbs = totalNutrients[u'CHOCDF'][u'quantity']
    else:
        return
    if u'FAT' in totalNutrients:
        fat = totalNutrients[u'FAT'][u'quantity']
    else:
        return
    if u'PROCNT' in totalNutrients:
        protein = totalNutrients[u'PROCNT'][u'quantity']
    else:
        return
    name = item[u'label']
    stages = map(lambda st: str(st), item[u'stages'])
    return Recipe(calories, carbs, fat, protein, stages, name, str(id))


def print_ration(ration):
    for meal in ration:
        print '---------------------------------'
        print meal.stage
        print 'Serving: ' + str(meal.serving)
        print 'Name: ' + meal.recipe.name
        print 'Calories: ' + str(meal.recipe.calories)
        print 'Carbs: ' + str(meal.recipe.carbs)
        print 'Fat: ' + str(meal.recipe.fat)
        print 'Protein: ' + str(meal.recipe.protein)
        print '---------------------------------'
    best_nutrion = get_ration_nutrion(ration)
    print '-------------SUMMARY-------------'
    print '-----------RESULT----TARGET------'
    print 'Calories  |' + str(best_nutrion[0]) + " | " + str(oat_data['target'][0])
    print 'Carbs     |' + str(best_nutrion[1]) + " | " + str(oat_data['target'][1])
    print 'Fat       |' + str(best_nutrion[2]) + " | " + str(oat_data['target'][2])
    print 'Protein   |' + str(best_nutrion[3]) + " | " + str(oat_data['target'][3])
    print '---------------------------------'


def main():
    print 'starting oat.meal!'
    # oat_data['population'] = 150
    # oat_data['ngen'] = 30
    print '-----------------TARGET-----------------'
    print "Cal/Carb/Fat/Protein|" + str([2000, 250, 120, 170])
    print '----------------------------------------'
    t0 = time.time()
    best = generate_ration([2000, 250, 120, 170])
    val, = evaluate_nutrion(best, [2000, 250, 120, 170])
    res = val / 100
    t1 = time.time()
    print '---------------PERFORMANCE--------------'
    print "Population          |" + str(oat_data['population'])
    print "NGEN                |" + str(oat_data['ngen'])
    print "Time total          |" + str(t1 - t0)
    print "Rank                |" + str(res)
    print "Cal/Carb/Fat/Protein|" + str(get_ration_nutrion(best))
    print '----------------------------------------'


def print_top_meals(best):
    for i in range(0, len(best.top_meals)):
        ration = best[::]
        top_meals_array = best.top_meals[i]
        for meal in top_meals_array:
            ration[i] = meal
            nutrion_m = get_ration_nutrion(ration)
            val_m, = evaluate_nutrion(ration, [2000, 250, 120, 170])
            rank_m = val_m / 100
            print '----------------------------------------'
            print "Replace for meal    |" + str(i)
            print "With recipe:        |" + meal.recipe.name
            print "Rank                |" + str(rank_m)
            print "Cal/Carb/Fat/Protein|" + str(nutrion_m)
            print '----------------------------------------'


if __name__ == "__main__":
    main()
    main()
    main()
    main()
