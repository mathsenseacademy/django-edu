from django.db import models
from django.utils import timezone

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    contact_number_1 = models.CharField(max_length=15)
    contact_number_2 = models.CharField(max_length=15, blank=True, null=True)

    student_class = models.CharField(max_length=50)
    school_or_college_name = models.CharField(max_length=255)
    board_or_university_name = models.CharField(max_length=255)

    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)

    notes = models.TextField(blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    student_id = models.CharField(max_length=20, unique=True, blank=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and not self.student_id:
            month = self.registered_at.strftime("%m")
            year = self.registered_at.strftime("%Y")
            self.student_id = f"MSA_{month}{year}{self.id}"
            Student.objects.filter(id=self.id).update(student_id=self.student_id)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"
