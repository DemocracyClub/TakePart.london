from django.contrib.gis.db import models


class BaseAreaModel(models.Model):
    gss = models.CharField(blank=True, max_length=100, db_index=True,
        unique=True)
    name = models.CharField(blank=True, max_length=100)
    population = models.IntegerField(blank=True, null=True)
    population_young = models.IntegerField(blank=True, null=True)
    population_voting_age = models.IntegerField(blank=True, null=True)
    growth_rate = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=4,
        max_digits=4)
    percent_registered = models.IntegerField(blank=True, null=True)
    registered_count = models.IntegerField(blank=True, null=True)
    area = models.MultiPolygonField(
        null=True, blank=True, srid=4326)

    @property
    def unregistered(self):
        return self.population_voting_age - self.registered_count

    class Meta:
        abstract = True


class Borough(BaseAreaModel):
    pass


class Ward(BaseAreaModel):
    borough = models.ForeignKey(Borough)


class LLSOA(BaseAreaModel):
    ward = models.ForeignKey(Ward, null=True)


class RegisteredPerson(models.Model):
    address = models.TextField(blank=True)
    address_hash = models.TextField(blank=True)
    postcode = models.CharField(blank=True, max_length=100, db_index=True)
    postcode_error = models.NullBooleanField(default=False)
    location = models.PointField(null=True, blank=True)
    ward = models.ForeignKey(Ward, null=True)
    borough = models.ForeignKey(Borough, null=True)
    borough_gss = models.CharField(blank=True, max_length=100, db_index=True)


class PostcodeCacheData(models.Model):
    postcode = models.CharField(blank=True, max_length=100, primary_key=True)
    ward_gss = models.CharField(max_length=30, null=True, db_index=True)
    borough_gss = models.CharField(max_length=30, null=True, db_index=True)
    location = models.PointField(null=True, blank=True)