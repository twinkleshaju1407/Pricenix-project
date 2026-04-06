from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    competitor_url = models.URLField(blank=True, null=True)

    our_price = models.FloatField()
    competitor_price = models.FloatField(blank=True, null=True)
    proposed_price = models.FloatField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    is_featured = models.BooleanField(default=True)
    rating = models.FloatField(default=4.2)  # demo rating

    # Sentiment Analysis Fields
    sentiment_score = models.FloatField(default=0.0)  # -1.0 to 1.0
    sentiment_label = models.CharField(max_length=20, default="Neutral")


    def discount_percentage(self):
        if self.competitor_price and self.our_price > self.competitor_price:
            return round(((self.our_price - self.competitor_price) / self.our_price) * 100)
        return 0



class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    old_price = models.FloatField()
    new_price = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected")
        ]
    )
    date = models.DateTimeField(auto_now_add=True)


class UiPathLog(models.Model):
    """Tracks UiPath bot execution history"""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESSFUL", "Successful"),
        ("FAULTED", "Faulted"),
    ]

    job_key = models.CharField(max_length=100, unique=True, blank=True, null=True)
    process_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    triggered_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    result_data = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-triggered_at"]
        verbose_name = "UiPath Log"
        verbose_name_plural = "UiPath Logs"

    def __str__(self):
        return f"{self.process_name} — {self.status} ({self.triggered_at:%Y-%m-%d %H:%M})"
