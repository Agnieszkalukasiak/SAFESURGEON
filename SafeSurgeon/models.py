from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.core.exceptions import ValidationError


# Create your models here.

class Verification(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    @classmethod
    def get_default_country(cls):
        default_country, _ = cls.objects.get_or_create(name='Default Country')
        return default_country
    
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}"
    
    @classmethod
    def get_default_city(cls):
        # Ensure a default country exists
        default_country, _ = Country.objects.get_or_create(name='Default Country')
        
        # Create or get the default city
        default_city, _ = cls.objects.get_or_create(name='Default City', country=default_country)
        return default_city

class Clinic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def default_clinic(cls):
        get_default_clinic, created = cls.objects.get_or_create(
            name="Default Clinic",
            defaults={'name': "Default Clinic"}
        )
        return default_clinic

#default user for development
def default_user_and_surgeon():
    #create or get default user
    default_user, created = User.objects.get_or_create(
        username='default_user', 
        defaults={
        'first_name': 'Default',
        'last_name': 'User',
        'email': 'default@example.com',
        'password':'defaultpassword' 
    })

    

    #create or get the dafult surgon liked to the default user
    default_surgeon,created = Surgeon.objects.get_or_create(
        user=default_user,
        defaults = {
            'profile_picture':'default_profile_pic.jpg',
            'clinic':'default clinic',
            'city':default_city,
            'country': default_country,
            'verification_status': Verification.PENDING,
            'id_document':'default_id_document.jpg',
            'slug':slugify(f"default-surgeon-{default_user.id}")
        }
    )
            #default education records
    Education.objects.get_or_create(
        surgeon=default_surgeon,
        institution="default university",
        program= "default program",
        institution_country ="institution country",
        start_date= '2001-02-02',
        end_date= '2004-02-02',
    )

    return default_surgeon

    #usage Uncomment for testing
#default_surgeon=default_user_and_surgeon()
#   print (default_surgeon.user_display())
#else:
#    print ("default_surgeon not found.")


class Surgeon(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="surgeon_verification")
    profile_picture = CloudinaryField('profile picture', folder='profilePicture', default='default_profile_pic', null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, related_name="surgeons")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="surgeon")
    country = models. ForeignKey(Country, on_delete=models.CASCADE, related_name="surgeon")
    verification_status = models.CharField(
        max_length=9, 
        choices=Verification.choices, 
        default=Verification.PENDING
    )
    id_document = CloudinaryField('Id', folder='Id', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user_first_name}-{self.user_last_name}")
    
        if not self.city or not self.country:
            default_country, _ = Country.objects.get_or_create(name='Default Country')
            default_city, _ = City.objects.get_or_create(name='Default City', country=default_country)
            
            if not self.city:
                self.city = default_city
            if not self.country:
                self.country = default_country
        
        super().save(*args, **kwargs) 


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_verification_status_display()}"
    
    def is_verified(self):
            return self.verification_status == Verification.VERIFIED

    def user_display(self):
        return {
            'name':f"{self.user.first_name} {self.user.last_name}",
            'email': self.user.email,
            'verification_status': self.get_verification_status_display(),
            'has_id_document': bool(self.id_document),
            'profile_picture_url': self.profile_picture.url if self.profile_picture else None,
            'clinic': self.clinic,
            'city': self.city.name if self.city else 'N/A',
            'country':self.country.name if self.country else 'N/A',
            'education': [f"{edu.institution} - {edu.program}" for edu in self.education.all()]
        }


class Education(models.Model):
    surgeon  = models.ForeignKey(Surgeon, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    program = models.CharField(max_length=200)
    institution_country = models.CharField(max_length=100, default='Unknown') 
    start_date = models.DateField()
    end_date = models.DateField()
    certificate = CloudinaryField('certificate', folder='certificates', null=True, blank=True)

   
    def clean(self):
       if self.start_date and self.end_date and self.start_date > self.end_date:
           raise ValidationError(_('End date must be after start date.'))

    def save(self, *args, **kwargs):
       self.full_clean()
       super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.institution} - {self.program} - {self.start_date} to {self.end_date}"

# class SurgeonVerification(models.Model):
#    user_first_name = models.CharField(max_length=100)
#    user_last_name = models.CharField(max_length=100)
 #   profile_picture = CloudinaryField('profile picture', folder='profilePicture', default='default_profile_pic', null=True, blank=True)
 #   clinic = models.CharField(max_length=100)
 #   city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="cities")            #this was just a charfield, can go back
 #   country = models. ForeignKey(Country, on_delete=models.CASCADE, related_name="countries") #this was just a charfield, can go back
 #   verification_status = models.CharField(
 #       max_length=9, 
 #       choices=Verification.choices, 
 #       default=Verification.PENDING
 #   )
 #   def __str__(self):
 #       return f"{self.first_name} {self.last_name} - {self.clinic}"
