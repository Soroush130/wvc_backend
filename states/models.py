from django.db import models
import pytz

class State(models.Model):
    """
    Represents a state entity with name, slug, abbreviation, latitude, and longitude.
    """

    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)
    is_active = models.BooleanField(default=True)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    zoom = models.PositiveSmallIntegerField(blank=True, default=8)

    def __str__(self) -> str:
        """
        Returns the string representation of the state.

        :return: The name of the state.
        """
        return self.name


class StateRoad(models.Model):
    state = models.ForeignKey(
        to="states.State",
        on_delete=models.CASCADE,
    )
    road = models.ForeignKey(
        to="states.Road",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.state.name}, {self.road.name}"


class Road(models.Model):
    """
    Represents a road entity associated with a state.
    """

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    states = models.ManyToManyField(to="states.State", through="states.StateRoad", related_name="roads")
    cities = models.ManyToManyField(to="states.City", through="states.CityRoad", related_name="roads")
    is_interstate = models.BooleanField(default=False)

    def __str__(self) -> str:
        """
        Returns the string representation of the road.

        :return: The name of the road.
        """
        return self.name


class CityRoad(models.Model):
    city = models.ForeignKey(
        to="states.City",
        on_delete=models.CASCADE,
    )
    road = models.ForeignKey(
        to="states.Road",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.city.name}, {self.road.name}"


class City(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32)
    abbreviation = models.CharField(max_length=6)
    timezone = models.CharField(
        max_length=17,
        blank=True,
        default="UTC",
        choices=[(tz, tz) for tz in filter(lambda t: t.startswith("US/"), pytz.all_timezones)],
    )
    state = models.ForeignKey(
        to="states.State",
        on_delete=models.CASCADE,
        related_name="cities",
    )
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    zoom = models.PositiveSmallIntegerField(blank=True, default=8)

    class Meta:
        verbose_name_plural = "cities"
        constraints = [
            models.UniqueConstraint(fields=["state", "name"], name="unique_name_per_state"),
            models.UniqueConstraint(fields=["state", "slug"], name="unique_slug_per_state"),
            models.UniqueConstraint(fields=["state", "abbreviation"], name="unique_abbreviation_per_state"),
        ]

    def __str__(self) -> str:
        return self.name
