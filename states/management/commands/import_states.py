import json
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from states.models import State


class Command(BaseCommand):
    help = 'Import states from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']

        with open(json_file, 'r') as f:
            states_data = json.load(f)

        created_count = 0
        updated_count = 0

        for index, state_data in enumerate(states_data, start=1):
            slug = slugify(state_data['name'])

            latitude = state_data.get('northLatitude') or 0.0
            longitude = state_data.get('westLongitude') or 0.0

            state, created = State.objects.update_or_create(
                abbreviation=state_data['abbreviation'],
                defaults={
                    'id': index,
                    'name': state_data['name'],
                    'slug': slug,
                    'is_active': state_data['active'],
                    'latitude': latitude,
                    'longitude': longitude,
                    'zoom': 8,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {state.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'⟳ Updated: {state.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nTotal: {created_count} created, {updated_count} updated'
        ))