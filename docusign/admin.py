from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'signer_name', 'signer_email', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('signer_name', 'signer_email', 'user')
