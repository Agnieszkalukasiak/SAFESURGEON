from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.text import slugify

# Create your models here.

class Verification(models.IntegerChoices):
    PENDING = 0, 'Pending'
    VERIFIED = 1, 'Verified'
    REJECTED = 2, 'Rejected'

class Country(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class Clinic (models.Model):
    name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="clinics")

class Surgeon(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="surgeon_verfication")
    profile_picture = CloudinaryField('profile picture', default='default_profile_pic')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="surgeons")
    verification_status = models.IntegerField(choices=Verification.choices, default=Verification.PENDING)
    created_on = models.DateTimeField(auto_now_add=True)
    id_document = models.FileField(upload_to='id_documents/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.name} - {self.get_verification_status_display()}"
    
    def user_display(self):
        return {
            'name': self.name,
            'email': self.email,
            'verification_status': self.get_verification_status_display(),
            'created_on': self.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            'has_id_document': bool(self.id_document),
            'profile_picture_url': self.profile_picture.url if self.profile_picture else None
        }

    class Meta:
        ordering = ['-created_on']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
    super().save(*args, **kwargs) 

    def __str__(self):
        return (f"{'Verified' if self.verification_status == Verification.VERIFIED else 'Not Verified'}, "
                f"{self.country.name if self.country else 'N/A'}, "
                f"{self.city.name if self.city else 'N/A'}, "
                f"{self.name}, "
                f"{self.clinic.name if self.clinic else 'N/A'}, "
                f"{', '.join(edu.program for edu in self.education.all())}")
    
    def user_display(self):
        return {
            'name': self.name,
            'email': self.email,
            'verification_status': self.get_verification_status_display(),
            'created_on': self.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            'has_id_document': bool(self.id_document),
            'profile_picture_url': self.profile_picture.url if self.profile_picture else None,
            'country': self.country.name if self.country else 'N/A',
            'city': self.city.name if self.city else 'N/A',
            'clinic': self.clinic.name if self.clinic else 'N/A',
            'education': [f"{edu.school} - {edu.program}" for edu in self.education.all()]
        }

class Education(models.Model):
    surgeon  = models.ForeignKey(Surgeon, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    program = models.CharField(max_length=200)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="educations")
    start_date = models.DateField()
    end_date = models.DateField()
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"{self.institution} - {self.program}"