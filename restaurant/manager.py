from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, employee_number, username, password, **extra_fields):
            values = [employee_number, username, password]
            field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))
            for field_name, value in field_value_map.items():
                if not value:
                    raise ValueError('The {} value must be set'.format(field_name))

            user = self.model(
                employee_number=employee_number,
                username=username,
                **extra_fields
            )
            user.set_password(password)
            user.save(using=self._db)
            return user

    def create_user(self, employee_number, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', False)
        return self._create_user(employee_number, username, password, **extra_fields)

    def create_superuser(self, employee_number, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self._create_user(employee_number, username, password, **extra_fields)

