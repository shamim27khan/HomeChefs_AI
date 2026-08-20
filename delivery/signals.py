from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .notifications import DeliveryNotificationSystem
from orders.models import DailyMealOrder

@receiver(post_save, sender=DailyMealOrder)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Notify delivery partners when an order becomes ready for delivery
    """
    if not created and instance.delivery_type == 'delivery':
        # Check if order status changed to 'ready'
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.order_status != 'ready' and instance.order_status == 'ready':
                # Notify available delivery partners
                DeliveryNotificationSystem.notify_available_partners(instance)
        except sender.DoesNotExist:
            # This is a new order, don't notify yet
            pass
