from django.contrib import admin
from .models import Course, Document, MultipleChoiceQuestion, ShortQuestion, Quiz

# Register your models here.
admin.site.register(Course)
admin.site.register(Document)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(ShortQuestion)
admin.site.register(Quiz)