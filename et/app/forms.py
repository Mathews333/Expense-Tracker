from django import forms
from .models import Expense, Category
from django.core.exceptions import ValidationError
from datetime import date

def apply_style(form):
    for field_name, field in form.fields.items():
        # Define base classes
        css_classes = 'form-control block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        
        # Add the classes to the existing widget attributes
        field.widget.attrs.update({'class': css_classes})

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'description', 'type']

        widgets = {
            # This 'type': 'date' is essential for the calendar picker
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }
        # def clean_amount(self):
        # amount = self.cleaned_data.get('amount')
        # if amount <= 0:
        #     raise ValidationError("Price must be greater than zero.")
        # return amount

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date > date.today():
            raise ValidationError("You cannot log a future expense.")
        return selected_date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_style(self) # This applies the CSS to all fields, including the date picker

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_style(self)
        
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

