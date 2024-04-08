from django.db import models
from django.conf import settings

# Create your models here.
class Match(models.Model): 
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='match_requests_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='match_requests_received', on_delete=models.CASCADE)
    matched_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('accepted', 'Accepted')), default='pending')

    def __str__(self):
        return f"{self.sender.username} and {self.receiver.username} - {self.status}"