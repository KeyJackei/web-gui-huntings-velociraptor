from django.db import models

class QueryVQL(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    query_vql = models.TextField()  # Многострочный запрос

    def __str__(self):
        return self.name