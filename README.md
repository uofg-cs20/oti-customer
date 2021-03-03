## CS20 Team Project Overview

**University of Glasgow - School of Computing Science - Third Year Team Project**

This project was to implement the Open Transport API and create a proof of concept of data sharing between two public transport operators. To do this we made two websites: Operator and Customer, both implementing their respective APIs. A user can log in to one instance of the Customer site, and link their account from another instance of the Customer site. This works by querying the Operator site to get the details of the second Customer instance, and then querying that Customer instance to retrieve the ticket data.

This repository contains the Customer website (aka Zebras), which implements the Customer API (https://app.swaggerhub.com/apis/open-transport/customer-account/1.0.1). It can be populated with dummy customer data, to illustrate the linking functionality. You can create an account on the Register page, or log in to your account on the Login page. Once logged in, there are 4 main pages:
- Purchase - for viewing and filtering purchased tickets
- Concession - for viewing and filtering purchased concessions
- Usage - for viewing and filtering past usages of tickets
- Connect - for linking accounts on other transport operator's sites

To connect another account simply select "Connect" on the desired transport operator on the Connect page, and enter the username and password of your remote account. This will cause tickets from the linked operator to appear in the Purchase, Concession and Usage pages. You can also unlink certain accounts by selecting "Disconnect" on the Connect page.

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
`python populate.py`

Run the server:  
`python manage.py runserver`  

Run tests:
`python manage.py test`

Log in as a customer (homepage):  
username: customer1 / customer2 (see population script)  
password: 1234  

Log in as website admin (/admin):  
username: dev  
password: 1234  

Customer API URL (need to be logged in):
/api
