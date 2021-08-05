from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favourite_name = models.CharField(blank=True, null=True, max_length=50, default="Saved Route")
    
    #Origin
    origin_name = models.CharField(max_length=225)
    origin_lat = models.FloatField()
    origin_lon = models.FloatField()

    #Destination
    destin_name = models.CharField(max_length=225)
    destin_lat = models.FloatField()
    destin_lon = models.FloatField()

    #Bus?
    stops = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'favourites'