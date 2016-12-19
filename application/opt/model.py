class Ration(list):
    def __getitem__(self, key):
        return list.__getitem__(self, key - 1)

    def get_meals(self):
        return self


class Meal:
    def __init__(self, recipe, serving, stage):
        self.recipe = recipe
        self.serving = serving
        self.stage = stage

    def get_nutrion(self):
        return self.recipe.calories * self.serving, self.recipe.carbs * self.serving, \
               self.recipe.fat * self.serving, self.recipe.protein * self.serving


class Recipe:
    def __init__(self, calories, carbs, fat, protein, stages, name, id):
        self.fat = fat
        self.protein = protein
        self.carbs = carbs
        self.calories = calories
        self.stages = stages
        self.name = name
        self.id = id

    def valid_stage(self, stage):
        return stage in self.stages
