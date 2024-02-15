from django import forms
from .models import *


class CategoryForm(forms.ModelForm):
    class Meta:
        model = category
        fields=['category_name']


class BrandFrom(forms.ModelForm):
    class Meta:
        model=Brand
        fields=['brand_name']


class ProductForm(forms.ModelForm):
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
        model=Product
        fields=['product_name','description','is_available','specifications','brand','category','featured','is_deleted']


