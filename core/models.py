from django.db import models
from utils.tools import generate_id

# Create your models here.
class Course(models.Model):
    COLOR_CHOICES = [
        ('black','Black')
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
    ]
    
    # Fields
    id = models.CharField(primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=50)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='red')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    id = models.CharField(primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=150)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    url = models.URLField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name