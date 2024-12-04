import csv
from django.shortcuts import render, redirect
from .models import Character
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import pandas as pd

def upload_csv(request):
    if request.method == "POST" and request.FILES['file']:
        csv_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        filepath = fs.url(filename)


        with open(filepath[1:], mode='r') as file:

            character_data = {}
            for line in file:

                line = line.strip()
                if ':' in line:
                    key, value = map(str.strip, line.split(':', 1))
                    character_data[key] = value


                if line == '':

                    if all(k in character_data for k in ['Name', 'Class', 'Position']):
                        Character.objects.create(
                            name=character_data['Name'],
                            character_class=character_data['Class'],
                            position=character_data['Position']
                        )

                    character_data = {}


            if character_data and all(k in character_data for k in ['Name', 'Class', 'Position']):
                Character.objects.create(
                    name=character_data['Name'],
                    character_class=character_data['Class'],
                    position=character_data['Position']
                )

        return redirect('character_list')
    return render(request, 'upload_csv.html')

def character_list(request):
    characters = Character.objects.all()
    return render(request, 'character_list.html', {'characters': characters})

def export_to_excel(request):
    characters = Character.objects.all().values()
    df = pd.DataFrame(list(characters))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=characters.xlsx'

    df.to_excel(response, index=False)
    return response


