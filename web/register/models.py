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

    def get_share_image_url(self):
        try:
            return self.shareimage.image.url
        except:
            return "/static/images/share_images/default_with_text_8_in_10.png"


class LLSOA(BaseAreaModel):
    ward = models.ForeignKey(Ward, null=True)

    population_young_2014 = models.IntegerField(blank=True, null=True)
    population_voting_age_2014 = models.IntegerField(blank=True, null=True)
    population_2014 = models.IntegerField(blank=True, null=True)

    @property
    def html_table(self):
        table_propties = (
            ('Population', self.population)
        )
        table = """
            <table>{}</table>
        """

        rows = []
        for k,v in table_propties:
            rows.append("""
            <tr>
                <th>{}</th>
                <td>{}</td>
            </tr>
            """.format(k,v))
        return table.format("".join(rows))


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
