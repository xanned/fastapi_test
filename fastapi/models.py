from tortoise import Model, fields


class TariffDB(Model):
    date = fields.DateField()
    cargo_type = fields.CharField(max_length=40)
    rate = fields.FloatField()

    class Meta:
        table = "tariffdb"
        unique_together = (("date", "cargo_type"),)
