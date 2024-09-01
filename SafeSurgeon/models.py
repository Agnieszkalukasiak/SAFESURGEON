from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.

class Verification(models.IntegerChoices):
    PENDING = 0, 'Pending'
    VERIFIED = 1, 'Verified'
    REJECTED = 2, 'Rejected'

class Surgeons(models.Model):
    Verification = ((0, "No"), (1, "Yes"))

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="surgeon_verifications")
    profile_picture = CloudinaryField('profile picture', default='default_profile_pic')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    verification_status = models.IntegerField(choices=Verification, default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    id_document = models.FileField(upload_to='id_documents/', null=True, blank=True)

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

class county(models.Models):
    country = models.CharField(max_length=100)

class city(models.Models):
    city = models.CharField(max_length=100)

class clinic (models.Models):
    clinic = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.author.username}'s Beautician Profile - {self.clinic}"

class Education(models.Model):
    beautician  = models.ForeignKey(Beauticians , related_name='education', on_delete=models.CASCADE)
    school = models.CharField(max_length=200)
    program = models.CharField(max_length=200)
    years = models.IntegerField()
    diploma = models.FileField(upload_to='diplomas/', null=True, blank=True)

def __str__(self):
    return f"{self.school} - {self.program}"

def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.name)
    super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.author.username}'s Beautician Profile - {self.clinic}"