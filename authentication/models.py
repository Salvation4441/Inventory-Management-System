from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone

# Create your user models
class CustomUser(AbstractUser):
   
    ROLE_CHOICES = [
        ('ADMIN', 'ADMIN'),
        ('SALESPERSON', 'SALESPERSON'),
    ]
    
    
    username = models.CharField(max_length=50,unique=True)
    first_name = models.CharField(max_length=30,null=True,blank=True)
    last_name = models.CharField(max_length=30,null=True,blank=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone  = models.CharField(max_length=15,null=True,blank=True)
    photo = models.ImageField(upload_to='profile/%Y/%m/%d/',null=True,blank=True)
    login_token = models.CharField(max_length=6, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='ADMIN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    
def generate_reset_token():
    return get_random_string(32)

# reset password
class PasswordResetRequest(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=64, default=generate_reset_token, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    TOKEN_VALIDITY_PERIOD = timezone.timedelta(hours=1)

    def is_valid(self):
        return timezone.now() <= self.created_at + self.TOKEN_VALIDITY_PERIOD

    def send_reset_email(self, request=None):
        if request:
            reset_link = request.build_absolute_uri(f"/reset-password/{self.token}/")
        else:
            reset_link = f"http://127.0.0.1:8000/reset-password/{self.token}/"
        send_mail(
            'Password Reset Request - Dreams POS',
            f'Hello,\n\nYou requested a password reset for your account. Click the link below to set a new password:\n{reset_link}\n\nThis link is valid for 1 hour.\nIf you did not make this request, you can safely ignore this email.',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )
        return reset_link
