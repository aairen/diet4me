from flask import Flask, render_template, request
import csv
from diet import Diet

app = Flask(__name__)

def read_diet_csv(file_name):
    diets = []
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            diets.append(Diet(
                name=row['Name'],
                characteristics=row['Key Characteristics'],
                foods=row['Foods'],
                protein_perc=row['Protein (%) per Day'],
                fat_perc=row['Fat (%) per Day'],
                carbs_perc=row['Carbs (%) per Day'],
                associated_diseases=row['Associated Disease'].split(', '),
                retained_char=row['Retained Characteristics'],
                incorporated_char=row['Incorporated Characteristics'],
                source=row['Source']
            ))
    return diets

def read_diet_meals_csv(file_name):
    diet_meals = {}
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            diet_meals[row['Diet Type']] = {
                'breakfast': row['Breakfast'],
                'lunch': row['Lunch'],
                'dinner': row['Dinner'],
                'snacks': row['Snacks']
            }
    return diet_meals

disease_data = {
    'African American': ['Hypertension', 'Cardiovascular disease', 'Type 2 diabetes', 'Obesity', 'Prostate cancer', 'Breast cancer', 'Neurodegenerative diseases', 'Epilepsy'],
    'Hispanic': ['Type 2 diabetes', 'Obesity', 'Cervical cancer', 'Liver cancer', 'Stomach cancer', 'Neurodegenerative diseases', 'Epilepsy'],
    'Caucasian': ['Obesity'],
    'Native American': ['Type 2 diabetes', 'Kidney cancer', 'Liver cancer', 'Lung and bronchus cancer', 'Cervical cancer', 'Colorectal cancer'],
    'Asian American': ['Type 2 diabetes', 'Stomach cancer', 'Liver cancer'],
}

diets = read_diet_csv('diet_database.csv')
diet_meals = read_diet_meals_csv('diet_meals.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_diet = None
    diet_meals_selected = None
    recommended_diets = []
    blue_zone = False
    macronutrient_message = None

    if request.method == 'POST':
        gender = request.form.get('gender')
        race = request.form.get('race')

        possible_diseases = disease_data.get(race, [])

        if race == 'Caucasian' and gender == 'Female':
            possible_diseases.append('High cholesterol')
        elif race == 'Hispanic' and gender == 'Male':
            possible_diseases.append('High cholesterol')

        recommended_diets = [diet for diet in diets if any(disease in diet.associated_diseases for disease in possible_diseases)]

        if 'diet' in request.form:
            selected_diet_name = request.form.get('diet')
            selected_diet = next((diet for diet in recommended_diets if diet.name == selected_diet_name), None)
            diet_meals_selected = diet_meals.get(selected_diet_name)

            if (selected_diet.protein_perc == 'N/A' or
                selected_diet.fat_perc == 'N/A' or
                selected_diet.carbs_perc == 'N/A'):
                macronutrient_message = "This diet does not require counting macronutrient proportions."

        if 'blue_zone' in request.form:
            blue_zone = True

    return render_template('index.html', all_diets=diets, diets=recommended_diets, diet=selected_diet, diet_meals=diet_meals_selected, blue_zone=blue_zone, selected_diet=selected_diet, macronutrient_message=macronutrient_message)

if __name__ == '__main__':
    app.run(debug=True)