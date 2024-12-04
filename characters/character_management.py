# character_management.py
from .models import Character

MAX_TANKS = 2
MAX_HEALS = 2
POSITION_CLASS_MAP = {
    'Tank': ['Paladin', 'Warrior'],
    'Heal': ['Shaman', 'Paladin', 'Druid'],
    'Ranged_Dps': ['Warlock', 'Mage', 'Shaman'],
    'Melee_Dps': ['Warrior', 'Paladin', 'Druid'],
}

class BaseCharacter:
    def __init__(self, name, character_class, position, user):
        self.name = name
        self.character_class = character_class
        self.position = position
        self.user = user

class CharacterValidator:
    @staticmethod
    def is_valid_position_class(position, character_class):
        return position in POSITION_CLASS_MAP and character_class in POSITION_CLASS_MAP[position]

    @staticmethod
    def name_starts_with_capital(name):
        return name and name[0].isupper()

    @staticmethod
    def validate(character_data, names_set, tank_count, heal_count):
        errors = []
        name = character_data.get('Name')

        if not CharacterValidator.name_starts_with_capital(name):
            errors.append('Name must start with a capital letter.')

        if name in names_set:
            errors.append(f"Names cannot be the same: {name}")
        else:
            names_set.add(name)

        if not CharacterValidator.is_valid_position_class(character_data.get('Position'), character_data.get('Class')):
            errors.append(f"{character_data['Class']} cannot be a {character_data['Position']}.")

        if tank_count > MAX_TANKS:
            errors.append("There cannot be more than 2 Tanks.")
        if heal_count > MAX_HEALS:
            errors.append("There cannot be more than 2 Healers.")

        return errors

class CharacterManager:
    @staticmethod
    def create_character(character_data, user):
        return Character.objects.create(
            name=character_data['Name'],
            character_class=character_data['Class'],
            position=character_data['Position'],
            user=user
        )

    @staticmethod
    def count_characters_by_position(user, position):
        return Character.objects.filter(position=position, user=user).count()
