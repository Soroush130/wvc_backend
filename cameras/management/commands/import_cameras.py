import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from states.models import State, City, Road
from cameras.models import Camera
import re


class Command(BaseCommand):
    help = 'Import cameras from JSON files in data/Cameras directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            type=str,
            default='data/Cameras',
            help='Path to Cameras directory (default: data/Cameras)'
        )

    def handle(self, *args, **options):
        Camera.objects.all().delete()

        cameras_dir = options['dir']

        if not os.path.exists(cameras_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {cameras_dir}'))
            return

        # پیدا کردن تمام فایل‌های JSON
        json_files = list(Path(cameras_dir).glob('*.json'))

        if not json_files:
            self.stdout.write(self.style.WARNING(f'No JSON files found in {cameras_dir}'))
            return

        self.stdout.write(f'Found {len(json_files)} JSON file(s)\n')

        created_count = 0
        updated_count = 0
        error_count = 0
        city_created_count = 0
        road_created_count = 0

        # ایجاد road پیش‌فرض
        default_road, created = Road.objects.get_or_create(
            slug='unknown-road',
            defaults={
                'name': 'Unknown Road',
                'is_interstate': False
            }
        )
        if created:
            self.stdout.write(f'Created default road: {default_road.name}\n')

        for json_file in json_files:
            self.stdout.write(f'\nProcessing: {json_file.name}')

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    cameras_data = json.load(f)

                for camera_data in cameras_data:
                    try:
                        # استخراج state و city از locationId (مثلاً MD_RU)
                        location_id = camera_data.get('locationId', '')
                        if not location_id or '_' not in location_id:
                            self.stdout.write(self.style.ERROR(
                                f'  ✗ {camera_data.get("name", "Unknown")}: Invalid locationId format'
                            ))
                            error_count += 1
                            continue

                        state_abbr, city_abbr = location_id.split('_', 1)

                        # پیدا کردن State
                        try:
                            state = State.objects.get(abbreviation=state_abbr)
                        except State.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'  ✗ {camera_data.get("name")}: State "{state_abbr}" not found'
                            ))
                            error_count += 1
                            continue

                        # پیدا کردن یا ایجاد City
                        try:
                            city = City.objects.get(state=state, abbreviation=city_abbr)
                        except City.DoesNotExist:
                            # ایجاد City جدید
                            city_name = f"{state.name} {city_abbr}"
                            city = City.objects.create(
                                state=state,
                                name=city_name,
                                slug=slugify(city_name),
                                abbreviation=city_abbr,
                                timezone='US/Eastern',  # می‌توانید بر اساس state تغییر دهید
                                latitude=camera_data.get('latitude', 0.0),
                                longitude=camera_data.get('longitude', 0.0),
                                zoom=12
                            )
                            city_created_count += 1
                            self.stdout.write(self.style.WARNING(
                                f'  ⊕ Auto-created city: {city.name} ({state.abbreviation})'
                            ))

                        # استخراج road از نام
                        name = camera_data.get('name', '')
                        road = None

                        # سعی در استخراج نام road از نام camera
                        if 'I-' in name or '(I-' in name:
                            match = re.search(r'I-(\d+)', name)
                            if match:
                                road_name = f'I-{match.group(1)}'
                                road, created = Road.objects.get_or_create(
                                    slug=slugify(road_name),
                                    defaults={
                                        'name': road_name,
                                        'is_interstate': True
                                    }
                                )
                                if created:
                                    road_created_count += 1
                        elif 'US ' in name or '(US ' in name:
                            match = re.search(r'US (\d+)', name)
                            if match:
                                road_name = f'US {match.group(1)}'
                                road, created = Road.objects.get_or_create(
                                    slug=slugify(road_name),
                                    defaults={
                                        'name': road_name,
                                        'is_interstate': False
                                    }
                                )
                                if created:
                                    road_created_count += 1
                        elif 'MD ' in name or '(MD ' in name:
                            match = re.search(r'MD (\d+)', name)
                            if match:
                                road_name = f'MD {match.group(1)}'
                                road, created = Road.objects.get_or_create(
                                    slug=slugify(road_name),
                                    defaults={
                                        'name': road_name,
                                        'is_interstate': False
                                    }
                                )
                                if created:
                                    road_created_count += 1

                        # اگر road پیدا نشد، از default استفاده کن
                        if not road:
                            road = default_road

                        # ایجاد slug یکتا
                        slug = slugify(name)

                        # اگر slug تکراری بود، id را به آن اضافه کن
                        if Camera.objects.filter(slug=slug).exclude(name=name).exists():
                            slug = f"{slug}-{camera_data.get('id', '')}"

                        # به‌روزرسانی یا ایجاد
                        camera, created = Camera.objects.update_or_create(
                            name=name,
                            defaults={
                                'slug': slug,
                                'url': camera_data.get('videoStreamUrl', ''),
                                'latitude': camera_data.get('latitude', 0.0),
                                'longitude': camera_data.get('longitude', 0.0),
                                'road': road,
                                'city': city,
                                'last_connection_status': False,
                            }
                        )

                        if created:
                            created_count += 1
                            if created_count % 100 == 0:  # هر 100 تا یک پیام
                                self.stdout.write(self.style.SUCCESS(
                                    f'  Progress: {created_count} cameras created...'
                                ))
                        else:
                            updated_count += 1

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f'  ✗ Error processing {camera_data.get("name", "unknown")}: {str(e)}'
                        ))

            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Invalid JSON in {json_file.name}: {str(e)}'))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error reading {json_file.name}: {str(e)}'))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{"=" * 50}'
            f'\nTotal: {created_count} cameras created, {updated_count} updated, {error_count} errors'
            f'\nAuto-created: {city_created_count} cities, {road_created_count} roads'
        ))