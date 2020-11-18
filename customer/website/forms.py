from django import forms


class RegisterForm(forms.Form):
    pass

class LoginForm(forms.Form):
    pass

class ConnectForm(forms.Form):
    pass
    
class FilterTickets(forms.Form):
    startdate = forms.CharField(label="Start Date")
    enddate = forms.CharField(label="End Date")