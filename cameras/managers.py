from django.conf import settings
from django.db.models import Q
from django.db.models.manager import Manager


class DetectedObjectManager(Manager):
    def above_confidence_level(self):
        ABOVE_CONFIDENCE_THRESHOLD = Q()
        for class_name, value in settings.YOLO_WORLD_MODEL_CLASSES.items():
            threshold = value.get("MINIMUM_CONFIDENCE_THRESHOLD")
            if threshold is not None:
                ABOVE_CONFIDENCE_THRESHOLD |= Q(name=class_name) & Q(conf__gte=threshold)
            else:
                ABOVE_CONFIDENCE_THRESHOLD |= Q(name=class_name)
        return self.get_queryset().filter(ABOVE_CONFIDENCE_THRESHOLD)