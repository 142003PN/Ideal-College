from django.db import models
from decimal import Decimal
from Students.models import Student
from Programs.models import Programs
from Academics.models import YearOfStudy, Semester
import uuid

# STUDENT ACCOUNT
class StudentAccount(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student} | Balance K{self.balance}'

# FEES
class Fee(models.Model):
    class FeeType(models.TextChoices):
        TUITION = 'Tuition'
        REGISTRATION = 'Registration'
        EXAM = 'Examination'
        LAB = 'Laboratory'
        NCZ = 'NCZ'

    class Scope(models.TextChoices):
        ALL = 'ALL', 'All Students'
        Programs = 'Programs', 'Programs Specific'

    fee_type = models.CharField(max_length=30, choices=FeeType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    scope = models.CharField(
        max_length=12,
        choices=Scope.choices,
        default=Scope.Programs
    )

    Programs = models.ForeignKey(
        Programs,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    year_of_study = models.ForeignKey(YearOfStudy, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.fee_type} - K{self.amount}'


# INVOICE (CHARGE DOCUMENT)
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=30, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invoice #{self.id} - K{self.amount}'
# PAYMENT (RECEIPT)
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    reference = models.CharField(max_length=100, blank=True)
    paid_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment K{self.amount} - {self.account.student}'


class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        DEBIT = 'DEBIT'
        CREDIT = 'CREDIT'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        StudentAccount,
        related_name='ledger_entries',
        on_delete=models.CASCADE
    )
    invoice = models.OneToOneField(
        Invoice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    entry_type = models.CharField(max_length=6, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # Reversal support
    is_reversal = models.BooleanField(default=False)
    reversed_entry = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reversals'
    )

    def __str__(self):
        return f'{self.entry_type} K{self.amount}'

# APPLIED FEES (ANTI-DUPLICATE)
class AppliedFee(models.Model):
    account = models.ForeignKey(StudentAccount, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    is_reversed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('account', 'fee', 'semester', 'is_reversed')  # include semester

    def __str__(self):
        status = "REVERSED" if self.is_reversed else "ACTIVE"
        return f'{self.fee} → {self.account.student} ({status})'

