import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from polls.models import Poll, Option, Vote
from django.utils import timezone
from datetime import timedelta

def populate_database():
    # Create test users
    admin = User.objects.create_user(
        username='admin',
        email='admin@chaguasmart.com',
        password='admin123',
        is_admin=True,
        campus='Main'
    )
    
    student1 = User.objects.create_user(
        username='student1',
        email='student1@chaguasmart.com',
        password='student123',
        campus='Main'
    )
    
    student2 = User.objects.create_user(
        username='student2',
        email='student2@chaguasmart.com',
        password='student123',
        campus='North'
    )
    
    # Create a poll
    poll = Poll.objects.create(
        title='Student President Election 2024',
        description='Vote for your next student body president',
        created_by=admin,
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(days=7)
    )
    
    # Add options
    option1 = Option.objects.create(poll=poll, text='Alice Johnson')
    option2 = Option.objects.create(poll=poll, text='Bob Smith')
    option3 = Option.objects.create(poll=poll, text='Carol Davis')
    
    # Add some votes
    Vote.objects.create(user=student1, poll=poll, option=option1)
    Vote.objects.create(user=student2, poll=poll, option=option2)
    
    print("Database populated successfully!")
    print(f"Created {User.objects.count()} users")
    print(f"Created {Poll.objects.count()} polls")
    print(f"Created {Option.objects.count()} options")
    print(f"Created {Vote.objects.count()} votes")

if __name__ == '__main__':
    populate_database()