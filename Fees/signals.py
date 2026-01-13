from decimal import Decimal
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from Registration.models import Registration
from Students.models import Student
from .models import (
    StudentAccount,
    Invoice,
    Payment,
    LedgerEntry,
    AppliedFee,
    Fee,
)

#create a student account when a student is created
@receiver(post_save, sender=Student)
def create_student_account(sender, instance, created, **kwargs):
    if created:
        StudentAccount.objects.create(id=instance.id, student=instance)


# INVOICE SIGNAL → DEBIT ACCOUNT (CHARGE STUDENT)
@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    account = instance.account
    amount = instance.amount

    # Description logic
    if instance.description:
        description = instance.description
    elif instance.fee:
        description = f'{instance.fee.fee_type} Fee'
    else:
        description = 'Manual Charge'

    with transaction.atomic():
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
            account.balance += amount
            account.save(update_fields=['balance'])

            # Only create AppliedFee when fee exists
            if instance.fee:
                AppliedFee.objects.get_or_create(
                    account=account,
                    fee=instance.fee
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

#Invoice a student automatically when the submmited courses are approved
@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)

    # Fire ONLY when status changes to Approved
    if previous_status == instance.status or instance.status != 'Approved':
        return

    student = instance.student_id
    year = instance.year_of_study
    program = student.profile.program

    # Get or create account
    account, _ = StudentAccount.objects.get_or_create(student=student)

    # Fetch applicable tuition fees
    tuition_fees = Fee.objects.filter(
        fee_type=Fee.FeeType.TUITION,
        Programs=program,
        year_of_study=year
    )

    with transaction.atomic():
        for fee in tuition_fees:

            # Prevent duplicate unless reversed
            if AppliedFee.objects.filter(
                account=account,
                fee=fee,
                is_reversed=False
            ).exists():
                continue

            # Create invoice ONLY (ledger + balance handled by signals)
            Invoice.objects.create(
                account=account,
                fee=fee,
                amount=fee.amount
            )
