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
    fee = instance.fee
    amount = instance.amount

    with transaction.atomic():
        ledger, ledger_created = LedgerEntry.objects.get_or_create(
            invoice=instance,
            defaults={
                'account': account,
                'entry_type': LedgerEntry.EntryType.DEBIT,
                'amount': amount,
                'description': f'{fee.fee_type} Fee (Invoice #{instance.id})'
            }
        )

        # Only touch balance & applied fee ONCE
        if ledger_created:
            account.balance += amount
            account.save(update_fields=['balance'])

            AppliedFee.objects.get_or_create(
                account=account,
                fee=fee
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
@receiver(pre_save, sender=Registration)
def registration_pre_save(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_status = (
            Registration.objects
            .filter(pk=instance.pk)
            .values_list('status', flat=True)
            .first()
        )
    else:
        instance._previous_status = None


@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)

    # Fire ONLY when status changes to Approved
    if previous_status == instance.status or instance.status != 'Approved':
        return

    account, _ = StudentAccount.objects.get_or_create(
        student=instance.student_id
    )

    registration_fee = Fee.objects.filter(
        fee_type='Registration'
    ).first()
    if not registration_fee:
        return

    amount = registration_fee.amount

    with transaction.atomic():
        # Invoice is the source of truth
        invoice, invoice_created = Invoice.objects.get_or_create(
            account=account,
            fee=registration_fee,
            defaults={'amount': amount}
        )

        # Ledger entry must be unique per invoice
        LedgerEntry.objects.get_or_create(
            account=account,
            invoice=invoice,
            entry_type=LedgerEntry.EntryType.DEBIT,
            defaults={
                'amount': amount,
                'description': f'{registration_fee.fee_type} Fee (Invoice #{invoice.id})'
            }
        )
