"""Hapus log kunjungan yang lebih lama dari batas retensi."""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from quran.models import AccessLog


class Command(BaseCommand):
    help = "Hapus log akses yang lebih lama dari STATS_RETENTION_DAYS hari."

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help="Override jumlah hari retensi (default dari settings).",
        )

    def handle(self, *args, **options):
        days = options['days']
        if days is None:
            days = getattr(settings, 'STATS_RETENTION_DAYS', 90)

        cutoff = timezone.now() - timedelta(days=days)
        deleted, _ = AccessLog.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"{deleted} log akses lebih lama dari {days} hari berhasil dihapus."
            )
        )
