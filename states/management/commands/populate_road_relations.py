from django.core.management.base import BaseCommand
from states.models import State, City, Road, StateRoad, CityRoad
from cameras.models import Camera


class Command(BaseCommand):
    help = 'Populate StateRoad and CityRoad relations from Camera data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate road relations...\n')

        state_road_count = 0
        city_road_count = 0

        # دریافت تمام Camera ها
        cameras = Camera.objects.select_related('city', 'city__state', 'road').all()

        total = cameras.count()
        self.stdout.write(f'Processing {total} cameras...\n')

        # استفاده از set برای جلوگیری از تکراری
        state_roads = set()
        city_roads = set()

        for i, camera in enumerate(cameras, 1):
            if i % 1000 == 0:
                self.stdout.write(f'  Progress: {i}/{total}')

            # StateRoad
            state_roads.add((camera.city.state.id, camera.road.id))

            # CityRoad
            city_roads.add((camera.city.id, camera.road.id))

        # ایجاد StateRoad
        self.stdout.write('\nCreating StateRoad relations...')
        for state_id, road_id in state_roads:
            _, created = StateRoad.objects.get_or_create(
                state_id=state_id,
                road_id=road_id
            )
            if created:
                state_road_count += 1

        # ایجاد CityRoad
        self.stdout.write('Creating CityRoad relations...')
        for city_id, road_id in city_roads:
            _, created = CityRoad.objects.get_or_create(
                city_id=city_id,
                road_id=road_id
            )
            if created:
                city_road_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{"=" * 50}'
            f'\nStateRoad relations created: {state_road_count}'
            f'\nCityRoad relations created: {city_road_count}'
        ))