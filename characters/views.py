# views.py
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Character
from .character_management import CharacterValidator, CharacterManager, MAX_TANKS, MAX_HEALS
from django.http import HttpResponse
import pandas as pd
from io import StringIO

MAX_DISPLAYED_CHARACTERS = 10

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
                # Validate character data
                error_messages += CharacterValidator.validate(character_data, names_set, tank_count, heal_count)

                if 'Tank' in character_data.get('Position', ''):
                    tank_count += 1
                if 'Heal' in character_data.get('Position', ''):
                    heal_count += 1

                if error_messages:
                    character_data = {}
                    continue

                CharacterManager.create_character(character_data, request.user)
                character_data = {}

        # Final check for remaining character data
        if character_data and all(k in character_data for k in ['Name', 'Class', 'Position']):
            error_messages += CharacterValidator.validate(character_data, names_set, tank_count, heal_count)

            if not error_messages:
                CharacterManager.create_character(character_data, request.user)

        if error_messages:
            return render(request, 'upload_csv.html', {'error_messages': error_messages})

        return redirect('character_list')
    return render(request, 'upload_csv.html')

@login_required
def character_list(request):
    # Use the sorting method to display characters sorted by name
    characters = CharacterManager.sort_characters_by_name(request.user)[:MAX_DISPLAYED_CHARACTERS]
    # Aggregating character classes for display or analysis
    character_classes_count = CharacterManager.aggregate_character_classes(request.user)
    return render(request, 'character_list.html', {
        'characters': characters,
        'character_classes_count': character_classes_count,
    })

@login_required
def add_character(request):
    if request.method == "POST":
        name = request.POST.get('name').strip()
        character_class = request.POST.get('class')
        position = request.POST.get('position')

        if not CharacterValidator.name_starts_with_capital(name):
            return render(request, 'add_character.html', {
                'error_message': 'Name must start with a capital letter.'
            })

        if not CharacterValidator.is_valid_position_class(position, character_class):
            return render(request, 'add_character.html', {
                'error_message': f"{character_class} cannot be a {position}."
            })

        if Character.objects.filter(name=name, user=request.user).exists():
            return render(request, 'add_character.html', {
                'error_message': 'Names cannot be the same for the same user.'
            })

        if position == 'Tank' and CharacterManager.count_characters_by_position(request.user, 'Tank') >= MAX_TANKS:
            return render(request, 'add_character.html', {
                'error_message': 'There cannot be more than 2 Tanks.'
            })

        if position == 'Heal' and CharacterManager.count_characters_by_position(request.user, 'Heal') >= MAX_HEALS:
            return render(request, 'add_character.html', {
                'error_message': 'There cannot be more than 2 Healers.'
            })

        CharacterManager.create_character({'Name': name, 'Class': character_class, 'Position': position}, request.user)
        return redirect('character_list')

    return render(request, 'add_character.html')

@login_required
def delete_character(request, character_id):
    character = get_object_or_404(Character, id=character_id, user=request.user)
    character.delete()
    return redirect('character_list')

@login_required
def export_to_excel(request):
    # Use the export method from CharacterManager
    df = CharacterManager.export_characters_to_dataframe(request.user)

    if df.empty:
        return render(request, 'character_list.html', {
            'characters': [],
            'error_message': 'No characters available to export.'
        })

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
            login(request, user)
            return redirect('character_list')
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
            return redirect('character_list')
        else:
            return render(request, 'registration/login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('landing_page')

def landing_page(request):
    return render(request, 'landing_page.html')
