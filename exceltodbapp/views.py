import openpyxl

from django.forms import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
from .models import MyData

def validate_row(row):
    """ Validates a single row from the Excel sheet. """
    name, age, email = row
    
    errors = {}

    # Name validation
    if not name:
        errors['name'] = "Name is required"
    
    # Age validation (should be a number)
    if not age:
        errors['age'] = "Age is required"
    else:
        try:
            age = int(age)
        except ValueError:
            errors['age'] = "Age must be an integer"

    # Email validation (should be a valid email format)
    if not email:
        errors['email'] = "Email is required"
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = "Invalid email format"

    return errors

def read_excel(file):
    """ Reads the Excel file and returns data with validation results. """
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    data = []
    errors = []

    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        row_errors = validate_row(row)
        if row_errors:
            errors.append({'row': idx, 'errors': row_errors})
        else:
            data.append({
                'name': row[0],
                'age': row[1],
                'email': row[2]
            })
    
    return data, errors

def preview_excel_data(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            
            # Read and validate the Excel file data
            data, errors = read_excel(excel_file)

            # If there are errors, display them in the UI
            if errors:
                return render(request, 'preview.html', {
                    'data': data,
                    'errors': errors,
                    'excel_file': excel_file
                })
            else:
                # If no errors, proceed to confirmation
                return render(request, 'preview.html', {
                    'data': data,
                    'excel_file': excel_file
                })

    else:
        form = ExcelUploadForm()

    return render(request, 'upload.html', {'form': form})

def confirm_push(request):
    if request.method == 'POST':
        # Retrieve the data from the POST request
        data = request.POST.getlist('data')
        pklist = []
        # Iterate over data and save it to the database
        for item in data:
            # Since the data comes as strings, you need to split and process each item
            name, age, email = item.split(',')
            MyData.objects.create(name=name, age=int(age), email=email)
        
        return HttpResponse("Success")

    return redirect('upload')

def index(request):
    return render(request, 'index.html')