from django.db import models
from django.contrib.postgres.indexes import BrinIndex
from django.utils.timezone import now
from django.utils import timezone

from .expressions import ConvertToTimezone
from .managers import DetectedObjectManager

import pytz


class Camera(models.Model):
    """
    Represents a camera entity associated with a road.
    """

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    url = models.URLField()
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    last_connection_status = models.BooleanField(default=False, blank=True, editable=False)
    road = models.ForeignKey(
        to="states.Road",
        on_delete=models.CASCADE,
        related_name="cameras",
    )
    city = models.ForeignKey(
        to="states.City",
        on_delete=models.CASCADE,
        related_name="cameras",
    )

    def __str__(self) -> str:
        return self.name


def get_video_upload_path(instance, filename):
    """
    Returns the upload path for a video file.

    :param instance: The Video instance.
    :param filename: The original filename.
    :return: The upload path as a string.
    """
    return f"videos/{instance.camera.id}/{filename}"


class Video(models.Model):
    """
    Represents a video entity associated with a camera.
    """

    camera = models.ForeignKey(
        to=Camera,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    file = models.FileField(upload_to=get_video_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the video.

        :return: The file name of the video.
        """
        return self.file.name


def get_photo_upload_path(instance, filename):
    """
    Returns the upload path for a photo file.

    :param instance: The Photo instance.
    :param filename: The original filename.
    :return: The upload path as a string.
    """
    now = timezone.now().strftime("%Y%m%d-%H%M%S.jpg")
    return f"photos/{instance.camera.city.state.slug}/{instance.camera.city.slug}/{instance.camera.slug}/{now}"


def get_default_system_confidence_value():
    # System Confidence
    MONITOR_SYSTEM_CONFIDENCE = 0.8
    return MONITOR_SYSTEM_CONFIDENCE


class Photo(models.Model):
    """
    Represents a photo entity associated with a camera.
    """

    id = models.BigAutoField(primary_key=True)
    camera = models.ForeignKey(
        to=Camera,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    file = models.ImageField(max_length=255, upload_to=get_photo_upload_path, blank=True)
    state = models.ForeignKey(
        to="states.State",
        on_delete=models.PROTECT,
        related_name="photos",
    )
    city = models.ForeignKey(
        to="states.City",
        on_delete=models.PROTECT,
        related_name="photos",
    )
    timezone = models.CharField(
        max_length=17,
        choices=[(tz, tz) for tz in filter(lambda t: t.startswith("US/"), pytz.all_timezones)],
    )
    timezone.empty_strings_allowed = False
    road = models.ForeignKey(
        to="states.Road",
        on_delete=models.PROTECT,
        related_name="photos",
    )
    system_confidence = models.FloatField(blank=True, default=get_default_system_confidence_value)
    connection_start_date = models.DateTimeField(blank=True, default=now)
    captured_at = models.DateTimeField(blank=True, default=now)
    local_captured_at = models.GeneratedField(
        expression=ConvertToTimezone("captured_at", "timezone"),
        output_field=models.DateTimeField(),
        db_persist=True,
    )
    detected_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    local_created_at = models.GeneratedField(
        expression=ConvertToTimezone("created_at", "timezone"),
        output_field=models.DateTimeField(),
        db_persist=True,
    )
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    car_count_above_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    car_count_below_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    truck_count_above_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    truck_count_below_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    person_count_above_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    person_count_below_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    deer_count_above_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    deer_count_below_system_confidence = models.PositiveSmallIntegerField(blank=True, default=0, editable=False)
    has_detected_objects = models.BooleanField(blank=True, default=False, editable=False)

    class Meta:
        indexes = [
            BrinIndex(fields=["local_created_at"]),
        ]

    def __str__(self) -> str:
        """
        Returns the string representation of the photo.

        :return: The file name of the photo if available.
        """
        return self.file.name if self.file else ""

    @property
    def is_connected(self):
        """
        Checks if the camera is connected at that moment.

        :return: Boolean indicating whether the camera was connected or not.
        """
        return bool(self.file)


def get_detected_object_upload_path(instance, filename):
    """
    Returns the upload path for a detected object image.

    :param instance: The DetectedObject instance.
    :param filename: The original filename.
    :return: The upload path as a string.
    """
    return f"objects/{instance.name}/{instance.photo.id}.jpg"


class DetectedObject(models.Model):
    """
    Represents an object detected within a photo captured by a camera.

    Attributes
    ----------
    id : BigAutoField
        The primary key for the detected object.
    photo : ForeignKey
        The photo in which the object was detected. References the Photo model and cascades on delete.
    name : CharField
        The name of the detected object (e.g., 'car', 'person', 'deer', 'truck'). Maximum length is 10 characters.
    image : ImageField
        The photo of the detected object.
    conf : FloatField
        The confidence score of the detection, typically between 0 and 1.
    x : FloatField
        The x-coordinate of the bounding box for the detected object.
        This value is calculated from the upper left corner of the photo and
        represents the upper left corner of the bounding box.
    y : FloatField
        The y-coordinate of the bounding box for the detected object.
        This value is calculated from the upper left corner of the photo and
        represents the upper left corner of the bounding box.
    width : FloatField
        The width of the bounding box for the detected object.
    height : FloatField
        The height of the bounding box for the detected object.
    captured_at : DateTimeField
        The timestamp when the detection was captured.
    created_at : DateTimeField
        The timestamp when the detection was created. Automatically set to the current date and time on creation.
    deleted_at : DateTimeField
        The timestamp when the detected object image was deleted.

    Methods
    -------
    __str__():
        Returns a string representation of the detected object, including its name and id.
    """

    class Name(models.TextChoices):
        DEER = "deer", "Deer"
        CAR = "car", "Car"
        TRUCK = "truck", "Truck"
        PERSON = "person", "Person"

    id = models.BigAutoField(primary_key=True)
    photo = models.ForeignKey(
        to=Photo,
        on_delete=models.CASCADE,
        related_name="detected_objects",
    )
    name = models.CharField(max_length=10, choices=Name)
    image = models.ImageField(
        max_length=255,
        upload_to=get_detected_object_upload_path,
        width_field="width",
        height_field="height",
    )
    conf = models.FloatField()
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    timezone = models.CharField(
        max_length=17,
        choices=[(tz, tz) for tz in filter(lambda t: t.startswith("US/"), pytz.all_timezones)],
    )
    timezone.empty_strings_allowed = False
    captured_at = models.DateTimeField(default=now)
    local_captured_at = models.GeneratedField(
        expression=ConvertToTimezone("captured_at", "timezone"),
        output_field=models.DateTimeField(),
        db_persist=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    local_created_at = models.GeneratedField(
        expression=ConvertToTimezone("created_at", "timezone"),
        output_field=models.DateTimeField(),
        db_persist=True,
    )
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = DetectedObjectManager()

    class Meta:
        verbose_name = "object"
        verbose_name_plural = "objects"
        indexes = [
            BrinIndex(fields=["local_created_at"]),
            models.Index(fields=["name", "conf"], name="detectedobject_name_conf_idx"),
        ]

    def __str__(self) -> str:
        """
        Returns the string representation of the detected object.

        Returns
        -------
        str
            The name of the detected object with its ID.
        """
        return f"{self.name.title()} {self.id}"
