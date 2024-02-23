from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

class SignUpForm(UserCreationForm):
    class Meta:
        model= CustomUser
        fields=['username','first_name','last_name','email','phone','password']

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = category
        fields=['category_name']
class TypeFrom(forms.ModelForm):
    class Meta:
        model=Type
        fields=['type_name']
class ProviderTypeForm(forms.ModelForm):
    class Meta:
        model=ProviderType
        fields=['provider_type_name','provider_type_code']
class ServiceForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        # for i, fields in self.fields.items():
        #     fields.widget.attrs['class'] = 'form-control'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Check if the field is a BooleanField and customize its rendering
            if isinstance(field, forms.BooleanField):
                field.widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
    class Meta:
        model=Service
        fields=['service_name','description','is_available','specifications','type','category','featured','is_deleted']
   
class ServiceImagesForm(forms.ModelForm):

    delete_image = forms.BooleanField(required=False, initial=False,widget=forms.HiddenInput)

    class Meta:
        model = ServiceImages
        fields = ['images']

    def __init__(self, *args, **kwargs):
        super(ServiceImagesForm, self).__init__(*args, **kwargs)
        self.fields['images'].required = False




class ServiceAttributeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.BooleanField):
                field.widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})

    class Meta:
        model = ServiceAttribute
        fields = ['service', 'provider_type', 'price','old_price', 'stock', 'image', 'is_deleted', 'is_available']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            try:
                # Attempt to validate the image extension
                image_extension = image.name.split('.')[-1].lower()
                valid_extensions = ['jpg', 'jpeg', 'png']
                if image_extension not in valid_extensions:
                    raise ValidationError("Only JPG, JPEG, and PNG files are allowed.")
            except AttributeError:
                # Handle the case where 'image' does not have a 'name' attribute
                raise ValidationError("Invalid image file.")
        return image
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError('Stock cannot be negative.')
        return stock
    





