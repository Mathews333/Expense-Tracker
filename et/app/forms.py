from django import forms
from .models import Expense, Category

def apply_style(form):
    for field_name, field in form.fields.items():
        # Define base classes
        css_classes = 'form-control block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        
        # Add the classes to the existing widget attributes
        field.widget.attrs.update({'class': css_classes})

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            # This 'type': 'date' is essential for the calendar picker
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }

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