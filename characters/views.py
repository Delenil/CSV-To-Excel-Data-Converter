from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
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

@login_required
def upload_csv(request):
    if request.method == "POST" and request.FILES['file']:
        csv_file = request.FILES['file']


        character_data = {}
        tank_count = 0
        heal_count = 0
        names_set = set()
        error_messages = []

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
                            position=character_data['Position'],
                            user=request.user
                        )

                character_data = {}


        if character_data and all(k in character_data for k in ['Name', 'Class', 'Position']):
            if character_data['Name'] in names_set:
                error_messages.append(f"Names cannot be the same: {character_data['Name']}")
            else:
                names_set.add(character_data['Name'])

            if 'Tank' in character_data.get('Position', ''):
                tank_count += 1
            if 'Heal' in character_data.get('Position', ''):
                heal_count += 1

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
                    position=character_data['Position'],
                    user=request.user  # Associate character with the logged-in user
                )

        if error_messages:
            return render(request, 'upload_csv.html', {'error_messages': error_messages})

        return redirect('character_list')
    return render(request, 'upload_csv.html')


@login_required
def character_list(request):
    characters = Character.objects.filter(user=request.user)[:MAX_DISPLAYED_CHARACTERS]
    return render(request, 'character_list.html', {'characters': characters})


@login_required
def add_character(request):
    if request.method == "POST":
        name = request.POST.get('name')
        character_class = request.POST.get('class')
        position = request.POST.get('position')

        if not character_is_valid(name, character_class, position):
            return render(request, 'add_character.html',
                          {'error_message': f"{character_class} cannot be a {position}."})

        if Character.objects.filter(name=name, user=request.user).exists():
            return render(request, 'add_character.html', {'error_message': 'Names cannot be the same for the same user.'})

        if position == 'Tank' and Character.objects.filter(position='Tank', user=request.user).count() >= MAX_TANKS:
            return render(request, 'add_character.html', {'error_message': 'There cannot be more than 2 Tanks.'})

        if position == 'Heal' and Character.objects.filter(position='Heal', user=request.user).count() >= MAX_HEALS:
            return render(request, 'add_character.html', {'error_message': 'There cannot be more than 2 Healers.'})

        Character.objects.create(name=name, character_class=character_class, position=position, user=request.user)
        return redirect('character_list')

    return render(request, 'add_character.html')


@login_required
def delete_character(request, character_id):
    character = get_object_or_404(Character, id=character_id, user=request.user)
    character.delete()
    return redirect('character_list')


@login_required
def export_to_excel(request):

    characters = Character.objects.filter(user=request.user)[:MAX_DISPLAYED_CHARACTERS].values()


    if not characters:

        return render(request, 'character_list.html', {
            'characters': [],
            'error_message': 'No characters available to export.'
        })


    df = pd.DataFrame(list(characters))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=characters.xlsx'

    df.to_excel(response, index=False)
    return response


# User registration and authentication views
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('character_list')  # Redirect to character list or any desired page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('character_list')  # Redirect after successful login
        else:
            return render(request, 'registration/login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('landing_page')

def landing_page(request):
    return render(request, 'landing_page.html')

