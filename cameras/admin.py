from django.contrib import admin
from import_export.admin import ImportExportMixin
from django.db.models import Count

from . import models


class PhotoTabularInline(admin.TabularInline):
    model = models.Photo
    fields = ("file", "created_at")
    readonly_fields = fields
    can_delete = False
    max_num = 3
    extra = 0


@admin.register(models.Camera)
class CameraAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "road",
        "total_deer",
        "total_cars",
        "total_trucks",
        "total_people",
        "total_connected",
        "total_disconnected",
        "total_photo",
    ]
    search_fields = ["name"]
    list_filter = ["city__state"]
    inlines = [PhotoTabularInline]
    prepopulated_fields = {"slug": ("name",)}

    @admin.display
    def total_deer(self, obj):
        return models.DetectedObject.objects.filter(name="deer", photo__camera=obj).count()

    @admin.display
    def total_cars(self, obj):
        return models.DetectedObject.objects.filter(name="car", photo__camera=obj).count()

    @admin.display
    def total_trucks(self, obj):
        return models.DetectedObject.objects.filter(name="truck", photo__camera=obj).count()

    @admin.display
    def total_people(self, obj):
        return models.DetectedObject.objects.filter(name="person", photo__camera=obj).count()

    @admin.display
    def total_connected(self, obj):
        return models.Photo.objects.filter(camera=obj).exclude(file="").aggregate(Count("id"))["id__count"]

    @admin.display
    def total_disconnected(self, obj):
        return models.Photo.objects.filter(camera=obj).filter(file="").aggregate(Count("id"))["id__count"]

    @admin.display
    def total_photo(self, obj):
        return models.Photo.objects.filter(camera=obj).aggregate(Count("id"))["id__count"]


@admin.register(models.Video)
class VideoAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["file", "camera"]
    search_fields = ["camera__name"]
    list_filter = ["camera__city__state"]


@admin.register(models.Photo)
class PhotoAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
        "file",
        "camera",
        "is_connected",
        "created_at",
    ]
    search_fields = ["camera__name"]
    list_filter = ["camera__city__state"]

    @admin.display(boolean=True)
    def is_connected(self, obj):
        return obj.is_connected


@admin.register(models.DetectedObject)
class DetectedObjectAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["name", "conf", "width", "height"]
    list_filter = ["name", "photo__created_at"]
