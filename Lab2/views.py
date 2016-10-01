import forms
import csv
import models

from django.shortcuts import render_to_response

# Create your views here.


def handle_uploaded_file(table_name, csv_file):
    reader = csv.DictReader(open(csv_file))
    for row in reader:
        models.add_record(table_name, row)


def tables(request):
    return render_to_response("tables.html", {"tables": models.get_tables_names()})


def add_dimension(request, table_name):
    if request.method == 'POST':
        form = forms.CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(table_name, request.FILES['file'])
    else:
        pass


def add_fact(request):
    return
