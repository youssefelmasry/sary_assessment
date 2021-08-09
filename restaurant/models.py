from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator

from restaurant.manager import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    employee_number = models.PositiveSmallIntegerField(unique=True, validators=[
        MinValueValidator(1000),
        MaxValueValidator(9999)
    ])
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'employee_number'
    REQUIRED_FIELDS = ['username', 'password']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} {self.employee_number}"


class Table(models.Model):
    table_number = models.PositiveSmallIntegerField(unique=True)
    table_number_of_seats = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1), 
        MaxValueValidator(12)
    ])

    def __str__(self):
        return str(self.table_number)


class Reservation(models.Model):
    table = models.ForeignKey("restaurant.Table", related_name="reservation", on_delete=models.SET_NULL, null=True)
    reserve_start_time = models.TimeField()
    reserve_end_time = models.TimeField()
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(f"reservation id {self.pk} for table {self.table.table_number}")
