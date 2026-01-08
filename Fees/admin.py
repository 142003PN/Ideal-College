from django.contrib import admin, messages
from django.db import transaction

from .models import (
    StudentAccount,
    Fee,
    Invoice,
    Payment,
    LedgerEntry,
    AppliedFee,
)


# STUDENT ACCOUNT ADMIN
@admin.register(StudentAccount)
class StudentAccountAdmin(admin.ModelAdmin):
    list_display = ('student', 'balance', 'updated_at')
    readonly_fields = ('balance', 'updated_at')
    search_fields = ('student__name',)


# FEE ADMIN
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('fee_type', 'amount', 'scope', 'Programs')
    list_filter = ('fee_type', 'scope', 'Programs')


# INVOICE ADMIN (READ ONLY)
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'fee', 'amount', 'issued_on')
    readonly_fields = ('issued_on',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# PAYMENT ADMIN
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'payment_method', 'reference', 'paid_on')
    readonly_fields = ('paid_on',)


# LEDGER ADMIN WITH REVERSAL ACTION
@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'entry_type',
        'amount',
        'description',
        'is_reversal',
        'created_at',
    )
    list_filter = ('entry_type', 'is_reversal', 'created_at')
    search_fields = ('account__student__name', 'description')
    readonly_fields = (
        'account',
        'entry_type',
        'amount',
        'description',
        'created_at',
        'is_reversal',
        'reversed_entry',
    )

    actions = ['reverse_transaction']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def reverse_transaction(self, request, queryset):
        reversed_count = 0

        for entry in queryset:
            if entry.is_reversal:
                continue

            if LedgerEntry.objects.filter(reversed_entry=entry).exists():
                continue

            with transaction.atomic():
                LedgerEntry.objects.create(
                    account=entry.account,
                    entry_type=(
                        LedgerEntry.EntryType.CREDIT
                        if entry.entry_type == LedgerEntry.EntryType.DEBIT
                        else LedgerEntry.EntryType.DEBIT
                    ),
                    amount=entry.amount,
                    description=f'Reversal of Ledger Entry #{entry.id}',
                    is_reversal=True,
                    reversed_entry=entry
                )
                reversed_count += 1

        self.message_user(
            request,
            f'{reversed_count} transaction(s) reversed successfully.',
            level=messages.SUCCESS
        )

    reverse_transaction.short_description = "Reverse selected transactions"


# APPLIED FEES ADMIN
@admin.register(AppliedFee)
class AppliedFeeAdmin(admin.ModelAdmin):
    list_display = ('account', 'fee', 'applied_on')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
