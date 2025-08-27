import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from hangarin.models import Category, Priority, Task, SubTask, Note, STATUS_CHOICES

fake = Faker()

class Command(BaseCommand):
    help = "Seed Hangarin with categories, priorities, tasks, subtasks, and notes."

    def add_arguments(self, parser):
        parser.add_argument("--tasks", type=int, default=20)
        parser.add_argument("--subtasks", type=int, default=40)
        parser.add_argument("--notes", type=int, default=40)
        parser.add_argument("--reset", action="store_true", help="Delete existing data first")

    def handle(self, *args, **opts):
        if opts["reset"]:
            Note.objects.all().delete()
            SubTask.objects.all().delete()
            Task.objects.all().delete()
            Category.objects.all().delete()
            Priority.objects.all().delete()

        # 1) base reference data
        priorities = ["High", "Medium", "Low", "Critical", "Optional"]
        categories = ["Work", "School", "Personal", "Finance", "Projects"]

        for p in priorities:
            Priority.objects.get_or_create(name=p)
        for c in categories:
            Category.objects.get_or_create(name=c)

        all_priorities = list(Priority.objects.all())
        all_categories = list(Category.objects.all())

        # 2) tasks
        tasks = []
        for _ in range(opts["tasks"]):
            deadline = timezone.make_aware(fake.date_time_this_month())
            t = Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                deadline=deadline,
                status=fake.random_element(elements=[s[0] for s in STATUS_CHOICES]),
                priority=random.choice(all_priorities),
                category=random.choice(all_categories),
            )
            tasks.append(t)

        # 3) subtasks
        for _ in range(opts["subtasks"]):
            task = random.choice(tasks)
            SubTask.objects.create(
                title=fake.sentence(nb_words=5),
                status=fake.random_element(elements=[s[0] for s in STATUS_CHOICES]),
                parent_task=task,
            )

        # 4) notes
        for _ in range(opts["notes"]):
            task = random.choice(tasks)
            Note.objects.create(task=task, content=fake.paragraph(nb_sentences=3))

        self.stdout.write(self.style.SUCCESS("Seeded Hangarin data successfully."))

