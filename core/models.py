from django.db import models
from nanoid import generate

# Create your models here.
class Course(models.Model):
    COLOR_CHOICES = [
        ('black','Black'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
    ]
    
    id = models.CharField(primary_key=True, default=generate, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default="No course description")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='red')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    id = models.CharField(primary_key=True, default=generate, editable=False)
    original_filename = models.CharField(max_length=200, default="file")
    description = models.CharField(max_length=200, default="No course description")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename

class MultipleChoiceQuestion(models.Model):
    id = models.CharField(primary_key=True, default=generate, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    choice_1 = models.CharField(max_length=250, default="")
    choice_2 = models.CharField(max_length=250, default="")
    choice_3 = models.CharField(max_length=250, default="")
    choice_4 = models.CharField(max_length=250, default="")
    correct_ans = models.IntegerField()

    def __str__(self):
        return self.question

class ShortQuestion(models.Model):
    id = models.CharField(primary_key=True, default=generate, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    correct_ans = models.CharField(max_length=500)

    def __str__(self):
        return self.question
    
class Quiz(models.Model):
    id = models.CharField(primary_key=True, default=generate, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    multiple_choice_questions = models.ManyToManyField(MultipleChoiceQuestion, blank=True)
    short_questions = models.ManyToManyField(ShortQuestion, blank=True)

    def __str__(self):
        return self.name

