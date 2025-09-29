from django.contrib import admin
from django.db.models import Count
from import_export.admin import ImportExportMixin

from . import models


@admin.register(models.State)
class StateAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "is_active",
        "total_cameras",
        "total_deer",
        "total_cars",
        "total_trucks",
        "total_people",
        "total_connected",
        "total_disconnected",
        "total_photo",
    ]
    list_editable = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    @admin.display
    def total_cameras(self, obj):
        return models.Camera.objects.filter(city__state=obj).count()

    @admin.display
    def total_deer(self, obj):
        return models.DetectedObject.objects.filter(name="deer", photo__camera__city__state=obj).count()

    @admin.display
    def total_cars(self, obj):
        return models.DetectedObject.objects.filter(name="car", photo__camera__city__state=obj).count()

    @admin.display
    def total_trucks(self, obj):
        return models.DetectedObject.objects.filter(name="truck", photo__camera__city__state=obj).count()

    @admin.display
    def total_people(self, obj):
        return models.DetectedObject.objects.filter(name="person", photo__camera__city__state=obj).count()

    @admin.display
    def total_connected(self, obj):
        return models.Photo.objects.filter(camera__city__state=obj).exclude(file="").aggregate(Count("id"))["id__count"]

    @admin.display
    def total_disconnected(self, obj):
        return models.Photo.objects.filter(camera__city__state=obj).filter(file="").aggregate(Count("id"))["id__count"]

    @admin.display
    def total_photo(self, obj):
        return models.Photo.objects.filter(camera__city__state=obj).aggregate(Count("id"))["id__count"]


@admin.register(models.Road)
class RoadAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "total_cameras",
        "total_deer",
        "total_cars",
        "total_trucks",
        "total_people",
        "total_connected",
        "total_disconnected",
        "total_photo",
    ]
    search_fields = ["name"]
    list_filter = ["states"]
    prepopulated_fields = {"slug": ("name",)}

    @admin.display
    def total_cameras(self, obj):
        return obj.cameras.count()

    @admin.display
    def total_deer(self, obj):
        return models.DetectedObject.objects.filter(name="deer", photo__camera__road=obj).count()

    @admin.display
    def total_cars(self, obj):
        return models.DetectedObject.objects.filter(name="car", photo__camera__road=obj).count()

    @admin.display
    def total_trucks(self, obj):
        return models.DetectedObject.objects.filter(name="truck", photo__camera__road=obj).count()

    @admin.display
    def total_people(self, obj):
        return models.DetectedObject.objects.filter(name="person", photo__camera__road=obj).count()

    @admin.display
    def total_connected(self, obj):
        return models.Photo.objects.filter(camera__road=obj).exclude(file="").aggregate(Count("id"))["id__count"]

    @admin.display
    def total_disconnected(self, obj):
        return models.Photo.objects.filter(camera__road=obj).filter(file="").aggregate(Count("id"))["id__count"]

    @admin.display
    def total_photo(self, obj):
        return models.Photo.objects.filter(camera__road=obj).aggregate(Count("id"))["id__count"]


@admin.register(models.StateRoad)
class StateRoadAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["road", "state"]
    list_filter = ["state"]


@admin.register(models.CityRoad)
class CityRoadAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["road", "city"]
    list_filter = ["city"]


@admin.register(models.City)
class CityAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["name", "abbreviation", "state"]
    search_fields = ["name"]
    list_filter = ["state"]
    prepopulated_fields = {"slug": ("name",)}