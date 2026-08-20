from django.contrib import admin
from django.utils.html import format_html
from .models import DeliveryPartner, DeliveryRequest, DeliveryAssignment, DeliveryRating

@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'phone_number', 'vehicle_type', 'vehicle_number', 
        'status', 'verification_status', 'is_available', 'total_deliveries', 
        'average_rating', 'created_at'
    ]
    list_filter = [
        'status', 'verification_status', 'is_available', 'vehicle_type', 
        'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'phone_number', 'vehicle_number']
    readonly_fields = ['total_deliveries', 'average_rating', 'completion_rate']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'phone_number', 'status', 'verification_status', 'is_available')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_number', 'license_number')
        }),
        ('Location', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update'),
            'classes': ('collapse',)
        }),
        ('Service Area', {
            'fields': ('service_areas', 'max_delivery_distance')
        }),
        ('Performance Metrics', {
            'fields': ('total_deliveries', 'average_rating', 'completion_rate'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_partners', 'activate_partners', 'deactivate_partners']
    
    def verify_partners(self, request, queryset):
        queryset.update(verification_status='verified')
        self.message_user(request, f'{queryset.count()} partners verified successfully.')
    verify_partners.short_description = 'Verify selected partners'
    
    def activate_partners(self, request, queryset):
        queryset.update(status='active', is_available=True)
        self.message_user(request, f'{queryset.count()} partners activated successfully.')
    activate_partners.short_description = 'Activate selected partners'
    
    def deactivate_partners(self, request, queryset):
        queryset.update(status='inactive', is_available=False)
        self.message_user(request, f'{queryset.count()} partners deactivated successfully.')
    deactivate_partners.short_description = 'Deactivate selected partners'

@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'partner_name', 'status', 'distance_km', 
        'delivery_fee', 'sent_at', 'expires_at'
    ]
    list_filter = ['status', 'sent_at', 'expires_at']
    search_fields = ['order__order_id', 'delivery_partner__user__username']
    readonly_fields = ['sent_at', 'responded_at']
    
    def order_id(self, obj):
        return obj.order.order_id if obj.order else 'N/A'
    order_id.short_description = 'Order ID'
    
    def partner_name(self, obj):
        return obj.delivery_partner.user.username if obj.delivery_partner else 'N/A'
    partner_name.short_description = 'Delivery Partner'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'delivery_partner__user')

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'partner_name', 'status', 'delivery_fee', 
        'partner_earnings', 'created_at', 'actual_delivery_time'
    ]
    list_filter = ['status', 'created_at', 'actual_delivery_time']
    search_fields = ['order__order_id', 'delivery_partner__user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def order_id(self, obj):
        return obj.order.order_id if obj.order else 'N/A'
    order_id.short_description = 'Order ID'
    
    def partner_name(self, obj):
        return obj.delivery_partner.user.username if obj.delivery_partner else 'N/A'
    partner_name.short_description = 'Delivery Partner'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order', 'delivery_partner', 'status')
        }),
        ('Addresses', {
            'fields': ('pickup_address', 'delivery_address')
        }),
        ('Timing', {
            'fields': (
                'estimated_pickup_time', 'estimated_delivery_time',
                'actual_pickup_time', 'actual_delivery_time'
            )
        }),
        ('Financial', {
            'fields': ('delivery_fee', 'partner_earnings')
        }),
        ('Location Tracking', {
            'fields': (
                'pickup_latitude', 'pickup_longitude',
                'delivery_latitude', 'delivery_longitude'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('pickup_notes', 'delivery_notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'delivery_partner__user')

@admin.register(DeliveryRating)
class DeliveryRatingAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'customer_name', 'rating', 'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = [
        'delivery_assignment__order__order_id', 
        'customer__username'
    ]
    readonly_fields = ['created_at']
    
    def order_id(self, obj):
        return obj.delivery_assignment.order.order_id if obj.delivery_assignment and obj.delivery_assignment.order else 'N/A'
    order_id.short_description = 'Order ID'
    
    def customer_name(self, obj):
        return obj.customer.username if obj.customer else 'N/A'
    customer_name.short_description = 'Customer'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'delivery_assignment__order', 
            'customer'
        )
