from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField('Student')


class Book(models.Model):
    name = models.CharField(max_length=100)
    pages = models.IntegerField(default=100)
    language = models.CharField(max_length=2, choices=[['en', 'Enligh'], ['de', 'German']])


class University(models.Model):
    name = models.CharField(max_length=50)
    library = models.ManyToManyField(Book)

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.name


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


