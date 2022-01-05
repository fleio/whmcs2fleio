from django.db import models


class TblproductUpgradeProducts(models.Model):
    product_id = models.IntegerField()
    upgrade_product_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblproduct_upgrade_products'
