from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'contact_name',
        'email',
        'status',
        'created_at',
    )

    search_fields = (
        'company_name',
        'email',
        'contact_name',
    )

    list_filter = (
        'status',
    )
	

# Register your models here.
