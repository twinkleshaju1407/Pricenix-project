from django.contrib import admin
from .models import Product, PriceHistory, UiPathLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'our_price', 'competitor_price', 'proposed_price', 'approved')
    list_filter = ('approved',)
    search_fields = ('name',)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'old_price', 'new_price', 'date')
    list_filter = ('date',)


@admin.register(UiPathLog)
class UiPathLogAdmin(admin.ModelAdmin):
    list_display = ('process_name', 'job_key', 'status', 'triggered_at', 'completed_at')
    list_filter = ('status', 'process_name')
    search_fields = ('job_key', 'process_name')
    readonly_fields = ('result_data', 'error_message')

