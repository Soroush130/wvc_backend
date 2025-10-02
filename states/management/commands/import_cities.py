import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from states.models import State, City


class Command(BaseCommand):
    help = 'Import cities from JSON files in data/Cities directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            type=str,
            default='data/Cities',
            help='Path to Cities directory (default: data/Cities)'
        )

    def handle(self, *args, **options):
        cities_dir = options['dir']

        if not os.path.exists(cities_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {cities_dir}'))
            return

        # پیدا کردن تمام فایل‌های JSON
        json_files = list(Path(cities_dir).glob('*.json'))

        if not json_files:
            self.stdout.write(self.style.WARNING(f'No JSON files found in {cities_dir}'))
            return

        self.stdout.write(f'Found {len(json_files)} JSON file(s)\n')

        created_count = 0
        updated_count = 0
        error_count = 0

        for json_file in json_files:
            self.stdout.write(f'\nProcessing: {json_file.name}')

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    cities_data = json.load(f)

                for city_data in cities_data:
                    try:
                        # پیدا کردن state از regionName
                        region_name = city_data.get('regionName')
                        if not region_name:
                            self.stdout.write(self.style.ERROR(
                                f'  ✗ {city_data.get("name")}: regionName is missing'
                            ))
                            error_count += 1
                            continue

                        try:
                            state = State.objects.get(name=region_name)
                        except State.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'  ✗ {city_data.get("name")}: State "{region_name}" not found'
                            ))
                            error_count += 1
                            continue

                        city_id = city_data.get('id', '')
                        if '_' in city_id:
                            abbreviation = city_id.split('_')[1]
                        else:
                            abbreviation = city_id[:6]  # حداکثر 6 کاراکتر

                        # ایجاد slug
                        slug = slugify(city_data['name'])

                        # به‌روزرسانی یا ایجاد
                        city, created = City.objects.update_or_create(
                            state=state,
                            abbreviation=abbreviation,
                            defaults={
                                'name': city_data['name'],
                                'slug': slug,
                                'timezone': city_data.get('timeZone', 'US/Eastern'),
                                'latitude': city_data.get('latitude', 0.0),
                                'longitude': city_data.get('longitude', 0.0),
                                'zoom': city_data.get('zoom', 12),
                            }
                        )

                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'  ✓ Created: {city.name} ({state.abbreviation})'
                            ))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.WARNING(
                                f'  ⟳ Updated: {city.name} ({state.abbreviation})'
                            ))

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f'  ✗ Error processing {city_data.get("name", "unknown")}: {str(e)}'
                        ))

            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Invalid JSON in {json_file.name}: {str(e)}'))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error reading {json_file.name}: {str(e)}'))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{"=" * 50}\nTotal: {created_count} created, {updated_count} updated, {error_count} errors'
        ))