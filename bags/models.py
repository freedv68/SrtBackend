from django.db import models

class BagDate(models.Model):
    id = models.BigAutoField(primary_key=True)
    bagDate = models.CharField(max_length=10, unique=True)

class BagPort(models.Model):
    id = models.BigAutoField(primary_key=True)
    bagDate = models.ForeignKey(
        "BagDate", on_delete=models.CASCADE, related_name='bagport')
    bagPort = models.CharField(max_length=10)

class BagNumber(models.Model):
    id = models.BigAutoField(primary_key=True)
    bagPort = models.ForeignKey(
        "BagPort", on_delete=models.CASCADE, related_name='bagnumber')
    bagNumber = models.IntegerField(default=0)

class BagHawbNo(models.Model):
    id = models.BigAutoField(primary_key=True)
    bagNumber = models.ForeignKey(
        "BagNumber", on_delete=models.CASCADE, related_name='baghawbno')
    bagHawbNo = models.CharField(max_length=20, unique=True)
    checked = models.BooleanField(default=False)
