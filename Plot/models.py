from django.db import models

# Create your models here.
class Table1(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    region_name = models.CharField(max_length=255)   # region mean state name or india
    financial_year = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.BigIntegerField(null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'exportexcel_table1'
        verbose_name_plural = "Table1"
    def __str__(self):
             return f"{self.state_name}"
    
class Table2(models.Model):
    id = models.AutoField(primary_key=True)
    mapone = models.ForeignKey(Table1, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    public = models.IntegerField()
    private = models.IntegerField()
    rural = models.IntegerField()
    urban = models.IntegerField()
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.BigIntegerField(null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'exportexcel_table2'
        verbose_name_plural = "Table1"
    def __str__(self):
             return f"{self.id}"

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)