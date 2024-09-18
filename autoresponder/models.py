from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')


# Model für GOZ
class GOZ(models.Model):
    goz_nummer = models.TextField(unique=True)
    uebersicht = models.TextField()
    beschreibung = models.TextField()
    kommentare = models.TextField()
    tags = models.TextField()
    ursachen_leistung = models.TextField()
    ursachen_patient = models.TextField()

    def __str__(self):
        return self.goz_nummer


class Muster(models.Model):
    muster_filename = models.TextField(unique=True)
    mustertext = models.TextField()
    titel = models.TextField()

    def __str__(self):
        return self.muster_filename


class GOZ_Muster(models.Model):
    goz = models.ForeignKey(GOZ, on_delete=models.CASCADE)
    muster = models.ForeignKey(Muster, on_delete=models.CASCADE)
    titel = models.TextField()

    def __str__(self):
        return f"{self.goz.goz_nummer} - {self.muster.muster_filename} - {self.titel}"


class GOZ_Urteile(models.Model):
    goz = models.ForeignKey(GOZ, on_delete=models.CASCADE)
    urteil_filename = models.TextField()
    titel = models.TextField()
    urteiltext = models.TextField()

    def __str__(self):
        return f"{self.goz.goz_nummer} - {self.urteil_filename} - {self.titel}"


class Generated_Record(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    status = models.TextField(default="IN_PROGRESS")
    input = models.TextField(null=True, blank=True)
    analog_input = models.TextField(null=True, blank=True)
    output = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True) 
    comment = models.TextField(null=True, blank=True)
    costs = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"ID: {self.id}, Input: {self.input}, Output: {self.output}, Rating: {self.rating}, Comment: {self.comment}"
    
class Analog(models.Model):
    id = models.AutoField(primary_key=True)
    beschreibung = models.TextField()

    def __str__(self):
        return f"ID: {self.id}, Beschreibung: {self.beschreibung}"   

