from django.db import models


class Paper(models.Model):
    title = models.CharField(max_length=500)  # Increased max length
    authors = models.CharField(max_length=500) # Store authors as a string
    file = models.FileField(upload_to='papers/', blank=True, null=True) # For optional file upload
    year = models.IntegerField()
    url = models.URLField(blank=True, null=True)
    further_information = models.TextField(blank=True, null=True)
    ai_summary = models.CharField(max_length=1000, blank=True, null=True)  # New field for AI summary

    def __str__(self):
        return f"{self.title} ({self.year}) - {self.authors}"