## CS20 Team Project

This repository contains the Customer website

## Installation  

Install requirements:  
`cd cs20-main`  
`pip install -r requirements.txt`  

Ensure database structure is up to date:  
`cd customer`  
`python manage.py makemigrations`  
`python manage.py migrate`  

## Viewing the Website

Run the population script:  
`python populate_cheetahs.py` or `python populate_zebras.py`

Run the server:  
`python manage.py runserver`  

Run tests:
`python manage.py test`

Log in as a customer (homepage):  
username: customer / customer2 (see population script)  
password: 1234  

Log in as website admin (/admin):  
username: dev  
password: 1234  

Customer API URL (need to be logged in):
/api
