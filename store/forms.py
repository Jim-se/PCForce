from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Review, Category

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'class': 'form-control'})
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        
class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = 'customer'

        if commit:
            user.save()

        return user


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = 'form-select' if field_name == 'category' else 'form-control'
            field.widget.attrs.update({'class': css_class})

    class Meta:
        model = Product
        fields = ['name', 'price', 'brand', 'category', 'image', 'description', 'code', 'stock']

class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Category
        fields = ['name']
