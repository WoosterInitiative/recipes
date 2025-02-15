from django.core.cache import caches

from cookbook.helper.cache_helper import CacheHelper
from cookbook.helper.unit_conversion_helper import UnitConversionHelper
from cookbook.models import PropertyType, Unit, Food, Property, Recipe, Step


class FoodPropertyHelper:
    space = None

    def __init__(self, space):
        """
        Helper to perform food property calculations
        :param space: space to limit scope to
        """
        self.space = space

    def calculate_recipe_properties(self, recipe):
        """
        Calculate all food properties for a given recipe.
        :param recipe: recipe to calculate properties for
        :return: dict of with property keys and total/food values for each property available
        """
        ingredients = []
        computed_properties = {}

        for s in recipe.steps.all():
            ingredients += s.ingredients.all()

        property_types = caches['default'].get(CacheHelper(self.space).PROPERTY_TYPE_CACHE_KEY, None)

        if not property_types:
            property_types = PropertyType.objects.filter(space=self.space).all()
            caches['default'].set(CacheHelper(self.space).PROPERTY_TYPE_CACHE_KEY, property_types, 60 * 60)  # cache is cleared on property type save signal so long duration is fine

        for fpt in property_types:
            computed_properties[fpt.id] = {'id': fpt.id, 'name': fpt.name, 'icon': fpt.icon, 'description': fpt.description, 'unit': fpt.unit, 'order': fpt.order, 'food_values': {}, 'total_value': 0, 'missing_value': False}

        uch = UnitConversionHelper(self.space)

        for i in ingredients:
            if i.food is not None:
                conversions = uch.get_conversions(i)
                for pt in property_types:
                    found_property = False
                    if i.food.properties_food_amount == 0 or i.food.properties_food_unit is None:
                        computed_properties[pt.id]['food_values'][i.food.id] = {'id': i.food.id, 'food': i.food.name, 'value': 0}
                        computed_properties[pt.id]['missing_value'] = i.food.properties_food_unit is None
                    else:
                        for p in i.food.properties.all():
                            if p.property_type == pt:
                                for c in conversions:
                                    if c.unit == i.food.properties_food_unit:
                                        found_property = True
                                        computed_properties[pt.id]['total_value'] += (c.amount / i.food.properties_food_amount) * p.property_amount
                                        computed_properties[pt.id]['food_values'] = self.add_or_create(computed_properties[p.property_type.id]['food_values'], c.food.id, (c.amount / i.food.properties_food_amount) * p.property_amount, c.food)
                    if not found_property:
                        computed_properties[pt.id]['missing_value'] = True
                        computed_properties[pt.id]['food_values'][i.food.id] = {'id': i.food.id, 'food': i.food.name, 'value': 0}

        return computed_properties

    # small dict helper to add to existing key or create new, probably a better way of doing this
    # TODO move to central helper ?
    @staticmethod
    def add_or_create(d, key, value, food):
        if key in d:
            d[key]['value'] += value
        else:
            d[key] = {'id': food.id, 'food': food.name, 'value': value}
        return d
