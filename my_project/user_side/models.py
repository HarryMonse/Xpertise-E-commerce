from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin,Group,Permission
from django.core.validators import FileExtensionValidator
from django.utils.safestring import mark_safe
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must an email address')
        if not username:
            raise ValueError('User must have a username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,first_name,last_name,username,email,password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(max_length=200,unique=True)
    phone = models.CharField(max_length=12,blank=True)

    #required fiels
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    objects=CustomUserManager()

    groups=models.ManyToManyField(Group,blank=True,related_name='home_user_groups')
    user_permissions=models.ManyToManyField(Permission,blank=True,related_name='home_user_permissions')
    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self,app_lebel):
        return True
    
class category(models.Model):
    category_name=models.CharField(max_length=100,unique=True)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) :
        return self.category_name
    
class Type(models.Model):
    type_name = models.CharField(max_length=255,unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) :
        return self.type_name
    
class ProviderType(models.Model):
    provider_type_name = models.CharField(max_length=100)
    provider_type_code = models.CharField(max_length=100)

    def provider_type_bg(self):
        return mark_safe('<div style="width:50px; height:50px; background-provider_type=%s"></div>' % (self.provider_type_code))

    def __str__(self):
        return self.provider_type_name


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    is_available=models.BooleanField(default=True)
    type = models.ForeignKey('Type', on_delete=models.CASCADE, default=1)
    category = models.ForeignKey('category', on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)
    specifications = models.TextField(null =True, blank =True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Products"

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def undo(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.product_name
    
    def get_percentage(self):
        new_price = (self.price /self.old_price) * 100
        return new_price

class ProductImages(models.Model):
    product = models.ForeignKey(Product ,related_name='product_image',on_delete=models.SET_NULL, null = True)
    images = models.ImageField(upload_to='photo/product_images3',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'], message="Only JPG, JPEG, and PNG files are allowed.")
                    ])
    date = models.DateTimeField(auto_now_add= True)
    
    class Meta:
        verbose_name_plural = "Product Images"

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    provider_type = models.ForeignKey(ProviderType, on_delete=models.CASCADE, default=1)
    price = models.PositiveIntegerField()
    stock = models.IntegerField(default=0)
    old_price = models.PositiveIntegerField(default=0)
    is_available=models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='photo/product_images',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'], message="Only JPG, JPEG, and PNG files are allowed.")
                    ],
                    default=timezone.now  # Example default value using timezone.now
                    )
    def __str__(self):
        return f"{self.product} - {self.provider_type} - ${self.price}"
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)
    







