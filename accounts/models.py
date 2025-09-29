from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    states = models.ManyToManyField(
        to="states.State",
        related_name="users",
        through="accounts.UserState",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserState(models.Model):
    user = models.ForeignKey(
        to="accounts.User",
        on_delete=models.CASCADE,
    )
    state = models.ForeignKey(
        to="states.State",
        on_delete=models.CASCADE,
    )
    default = models.BooleanField(blank=True, default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "state"], name="user_state_unique_together"),
            models.UniqueConstraint(
                fields=["user"], condition=models.Q(default=True), name="user_default_state_unique"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.state} - {self.user} ({'Default' if self.default else 'Non-default'})"
