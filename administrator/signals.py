from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F, FloatField
from .models import SalesItem, Sales


# ------------------------------------------
# UPDATE SALE TOTAL WHEN A SALES ITEM CHANGES
# ------------------------------------------
@receiver([post_save, post_delete], sender=SalesItem)
def update_sale_total(sender, instance, **kwargs):
    sale = instance.sale
    total = sale.items.aggregate(
        total=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
    )['total'] or 0.0

    if sale.total_amount != total:
        sale.total_amount = total
        sale.save(update_fields=['total_amount'])
