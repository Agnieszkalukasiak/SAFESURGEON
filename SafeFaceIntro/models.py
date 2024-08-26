from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    STATUS = ((0, "Draft"), (1, "Published"))

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification")
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    clinic_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.IntegerField(choices=STATUS, default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    id_document = models.FileField(upload_to='id_documents/', null=True, blank=True)
    diploma = models.FileField(upload_to='diplomas/', null=True, blank=True)

    def __str__(self):
        return f"{self.author.username}'s Post - {self.clinic_name}"

class Education(models.Model):
    post = models.ForeignKey(Post, related_name='education', on_delete=models.CASCADE)
    school = models.CharField(max_length=200)
    program = models.CharField(max_length=200)
    years = models.IntegerField()

    def __str__(self):
        return f"{self.school} - {self.program}"