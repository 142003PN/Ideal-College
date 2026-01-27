from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import uuid

from .models import Student, StudentAccount, Fee, Invoice, LedgerEntry, AppliedFee, Payment
from Registration.models import Registration

# CREATE STUDENT ACCOUNT
@receiver(post_save, sender=Student)
def create_student_account(sender, instance, created, **kwargs):
    if created:
        StudentAccount.objects.create(student=instance)


# INVOICE SIGNAL → DEBIT ACCOUNT
@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    account = instance.account
    amount = instance.amount

    # Use fee type or description for ledger
    if instance.fee:
        description = f'{instance.fee.fee_type} Fee'
    elif instance.description:
        description = instance.description
    else:
        description = "Invoice"

    with transaction.atomic():
        # Create ledger entry
        ledger, ledger_created = LedgerEntry.objects.get_or_create(
            invoice=instance,
            defaults={
                'account': account,
                'entry_type': LedgerEntry.EntryType.DEBIT,
                'amount': amount,
                'description': description
            }
        )

        if ledger_created:
            # Update account balance
            account.balance += amount
            account.save(update_fields=['balance'])

            # Track applied fee to prevent duplicates (semester-aware)
            if instance.fee and hasattr(instance, 'semester'):
                AppliedFee.objects.get_or_create(
                    account=account,
                    fee=instance.fee,
                    semester=instance.semester
                )


# PAYMENT SIGNAL → CREDIT ACCOUNT
@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    account = instance.account
    amount = instance.amount

    with transaction.atomic():
        # Ledger entry (CREDIT)
        LedgerEntry.objects.create(
            account=account,
            entry_type=LedgerEntry.EntryType.CREDIT,
            amount=amount,
            description=f'Payment via {instance.payment_method}'
        )

        # Update balance
        account.balance -= amount
        account.save(update_fields=['balance'])


# LEDGER REVERSAL SUPPORT
@receiver(post_save, sender=LedgerEntry)
def ledger_reversal_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.is_reversal or not instance.reversed_entry:
        return

    account = instance.account
    amount = instance.amount

    with transaction.atomic():
        if instance.entry_type == LedgerEntry.EntryType.DEBIT:
            account.balance += amount
        else:
            account.balance -= amount

        account.save(update_fields=['balance'])


# AUTO-INVOICE TUITION ON COURSE APPROVAL
@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)

    # Only fire when status changes to Approved
    if previous_status == instance.status or instance.status != 'Approved':
        return

    student = instance.student_id
    year = instance.year_of_study
    program = student.profile.program
    semester = instance.semester

    # Get or create student account
    account, _ = StudentAccount.objects.get_or_create(student=student)

    # Fetch tuition fees for this program & year
    tuition_fees = Fee.objects.filter(
        fee_type=Fee.FeeType.TUITION,
        Programs=program,
        year_of_study=year
    )

    with transaction.atomic():
        for fee in tuition_fees:
            # Skip if already applied for this semester and not reversed
            if AppliedFee.objects.filter(
                account=account,
                fee=fee,
                semester=semester,
                is_reversed=False
            ).exists():
                continue

            # Create invoice, attach semester so AppliedFee works
            invoice = Invoice.objects.create(
                account=account,
                fee=fee,
                amount=fee.amount,
            )
            # Attach semester dynamically for signals to use
            invoice.semester = semester
            invoice.save(update_fields=[])
