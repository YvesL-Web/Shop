from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# from django.core.validators import RegexValidator
# from django.utils.text import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
def get_profile_image_filepath(instance, filename):
    return 'profile_images/user_{0}/{1}'.format(instance.user.username, filename)

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        """
        Creates and saves a User with the 
        above listed parameter(first_name, last_name......).
        """
        if not email:
            raise ValueError("Users must have an email address!")
        if not username:
            raise ValueError("Users must have anusername!")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, password):
        """
        Creates and saves a superuser with the 
        above listed parameter(first_name, last_name......).
        """
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,  
        )
        user.is_admin = True
        user.is_active=True
        user.is_staff=True
        user.is_super_admin=True

        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    
    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to=get_profile_image_filepath, null=True, blank=True, default='default.jpg')  
    city = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.first_name
    
    def full_address(self):
        return f"{self.address}, {self.postal_code} {self.city}, {self.country}"
    
# Signal
@receiver(post_save, sender=Account)
def create_user_profile(instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)