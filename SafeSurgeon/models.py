from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.text import slugify



# Create your models here.

class Verification(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'


class Country(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}"

class Clinic (models.Model):
    name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="clinics")

    def __str__(self):
        return self.name

class Surgeon(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="surgeon_verification")
    profile_picture = CloudinaryField('profile picture', folder='profilePicture', default='default_profile_pic', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    clinic = models.CharField(max_length=255, null=True, blank=True)
    verification_status = models.CharField(
        max_length=9, 
        choices=Verification.choices, 
        default=Verification.PENDING
    )
    created_on = models.DateTimeField(auto_now_add=True)
    id_document = CloudinaryField('Id', folder='Id', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['-created_on']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}")
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_verification_status_display()}"
    
    def is_verified(self):
            return self.verification_status == Verification.VERIFIED

    def user_display(self):
        return {
            'name':f"{self.first_name} {self.last_name}",
            'email': self.email,
            'verification_status': self.get_verification_status_display(),
            'created_on': self.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            'has_id_document': bool(self.id_document),
            'profile_picture_url': self.profile_picture.url if self.profile_picture else None,
            'city': self.clinic.city.name if self.clinic else 'N/A',
            'clinic': self.clinic.name if self.clinic else 'N/A',
            'education': [f"{edu.institution} - {edu.program}" for edu in self.education.all()]
        }

class Education(models.Model):
    surgeon  = models.ForeignKey(Surgeon, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    program = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    certificate = CloudinaryField('certificate', folder='certificates', null=True, blank=True)

    def __str__(self):
        return f"{self.institution} - {self.program}"

class SurgeonVerification(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture = CloudinaryField('profile picture', folder='profilePicture', default='default_profile_pic', null=True, blank=True)
    clinic = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=9, 
        choices=Verification.choices, 
        default=Verification.PENDING
    )
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.clinic}"
