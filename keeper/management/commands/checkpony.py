import datetime
import logging

from django.core.management import BaseCommand, CommandError,CommandParser
from django.utils.timezone import now

from ...models import Pony,History
from ...services import notification


def mark_pony_missing(pony: Pony):
    pony.status = Pony.STATUS_MISSING
    pony.save()
    history = History(
        pony_id= pony.id,
        previous_status= Pony.STATUS_NORMAL,
        current_status=Pony.STATUS_MISSING,
        create_time=now()
    )
    history.save()
    notification.send_status_change_notification(pony, Pony.STATUS_NORMAL, Pony.STATUS_MISSING)


class Command(BaseCommand):
    help = "Check ponies who are losing contact and send notifications"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--dry-run', action='store_true',
                            help= 'just check ponies, without actual changing status or sending notifications')

    def handle(self, *args, **options):
        start_time = now()
        dry_run: bool = options['dry_run']
        self.stdout.write("start checking ponies")
        normal_ponies = Pony.objects.filter(status=Pony.STATUS_NORMAL)
        current_time = now()
        total_ponies = normal_ponies.count()
        missing_ponies = 0
        for pony in normal_ponies:
            if pony.last_hi_time is None:
                continue
            dark_delta = datetime.timedelta(minutes=pony.dark_minute + 5)
            if current_time - pony.last_hi_time > dark_delta:
                if not dry_run:
                    mark_pony_missing(pony)
                missing_ponies += 1
                logging.info("pony missing: %s , %d", pony.name, pony.dark_minute)

        time_cost = now() - start_time
        self.stdout.write(f"finished checking, total {total_ponies} ,missing {missing_ponies} , execution time: {time_cost.total_seconds()} s")
        if dry_run:
            self.stdout.write('dry-run option on, no changes will be made')