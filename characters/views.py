from django.shortcuts import render, redirect, get_object_or_404
from .models import Character
from django.http import HttpResponse
import pandas as pd
from io import StringIO


MAX_TANKS = 2
MAX_HEALS = 2
MAX_DISPLAYED_CHARACTERS = 10

# Allowed position-class mappings
POSITION_CLASS_MAP = {
    'Tank': ['Paladin', 'Warrior'],
    'Heal': ['Shaman', 'Paladin', 'Druid'],
    'Ranged_Dps': ['Warlock', 'Mage', 'Shaman'],
    'Melee_Dps': ['Warrior', 'Paladin', 'Druid'],
}


def character_is_valid(name, character_class, position):
    if position not in POSITION_CLASS_MAP:
        return False
    if character_class not in POSITION_CLASS_MAP[position]:
        return False
    return True


def upload_csv(request):
    if request.method == "POST" and request.FILES['file']:
        csv_file = request.FILES['file']

        # Read the CSV directly into a string
        character_data = {}
        tank_count = 0
        heal_count = 0
        names_set = set()
        error_messages = []

        # Use StringIO to read the file content without saving it
        file_content = StringIO(csv_file.read().decode('utf-8'))

        for line in file_content:
            line = line.strip()
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                character_data[key] = value

            if line == '':
                if character_data.get('Name') in names_set:
                    error_messages.append(f"Names cannot be the same: {character_data['Name']}")
                else:
                    names_set.add(character_data['Name'])

                if 'Tank' in character_data.get('Position', ''):
                    tank_count += 1
                if 'Heal' in character_data.get('Position', ''):
                    heal_count += 1

                # Validate character class and position
                if not character_is_valid(character_data.get('Name'), character_data.get('Class'),
                                          character_data.get('Position')):
                    error_messages.append(f"{character_data['Class']} cannot be a {character_data['Position']}.")

                if all(k in character_data for k in ['Name', 'Class', 'Position']):
                    if tank_count > MAX_TANKS:
                        error_messages.append("There cannot be more than 2 Tanks.")
                    if heal_count > MAX_HEALS:
                        error_messages.append("There cannot be more than 2 Healers.")

                    if not any(error_messages):
                        Character.objects.create(
                            name=character_data['Name'],
                            character_class=character_data['Class'],
                            position=character_data['Position']
                        )

                character_data = {}

        # Handle the last character if the file didn't end with a newline
        if character_data and all(k in character_data for k in ['Name', 'Class', 'Position']):
            if character_data['Name'] in names_set:
                error_messages.append(f"Names cannot be the same: {character_data['Name']}")
            else:
                names_set.add(character_data['Name'])

            if 'Tank' in character_data.get('Position', ''):
                tank_count += 1
            if 'Heal' in character_data.get('Position', ''):
                heal_count += 1

            # Validate character class and position
            if not character_is_valid(character_data.get('Name'), character_data.get('Class'),
                                      character_data.get('Position')):
                error_messages.append(f"{character_data['Class']} cannot be a {character_data['Position']}.")

            if tank_count > MAX_TANKS:
                error_messages.append("There cannot be more than 2 Tanks.")
            if heal_count > MAX_HEALS:
                error_messages.append("There cannot be more than 2 Healers.")

            if not any(error_messages):
                Character.objects.create(
                    name=character_data['Name'],
                    character_class=character_data['Class'],
                    position=character_data['Position']
                )

        if error_messages:
            return render(request, 'upload_csv.html', {'error_messages': error_messages})

        return redirect('character_list')
    return render(request, 'upload_csv.html')


def character_list(request):
    characters = Character.objects.all()[:MAX_DISPLAYED_CHARACTERS]  # Limit to MAX_DISPLAYED_CHARACTERS
    return render(request, 'character_list.html', {'characters': characters})


def add_character(request):
    if request.method == "POST":
        name = request.POST.get('name')
        character_class = request.POST.get('class')
        position = request.POST.get('position')

        if not character_is_valid(name, character_class, position):
            return render(request, 'add_character.html',
                          {'error_message': f"{character_class} cannot be a {position}."})

        if Character.objects.filter(name=name).exists():
            return render(request, 'add_character.html', {'error_message': 'Names cannot be the same.'})

        if position == 'Tank' and Character.objects.filter(position='Tank').count() >= MAX_TANKS:
            return render(request, 'add_character.html', {'error_message': 'There cannot be more than 2 Tanks.'})

        if position == 'Heal' and Character.objects.filter(position='Heal').count() >= MAX_HEALS:
            return render(request, 'add_character.html', {'error_message': 'There cannot be more than 2 Healers.'})

        Character.objects.create(name=name, character_class=character_class, position=position)
        return redirect('character_list')

    return render(request, 'add_character.html')


def delete_character(request, character_id):
    character = get_object_or_404(Character, id=character_id)
    character.delete()
    return redirect('character_list')


def export_to_excel(request):
    characters = Character.objects.all().values()
    df = pd.DataFrame(list(characters))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=characters.xlsx'

    df.to_excel(response, index=False)
    return response

