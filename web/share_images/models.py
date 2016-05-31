from django.contrib.gis.db import models


class GeographImage(models.Model):
    image_id = models.IntegerField(primary_key=True)
    location = models.PointField(null=True, blank=True)
    SON_AVG = models.FloatField()
    orig_image = models.ImageField(
        upload_to='images/geograph/',
        max_length=800,
        null=True)
    dream_image = models.ImageField(
        upload_to='images/dreams/',
        max_length=800,
        null=True)


class ShareImage(models.Model):
    ward = models.OneToOneField('register.Ward', primary_key=True)
    image = models.ImageField(
        upload_to='images/shares/',
        max_length=800,
        null=True)
