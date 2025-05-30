# Generated by Django 5.1.1 on 2025-04-21 06:28

from django.db import migrations

from Requests.models import QueryVQL


def load_artifacts(apps, schema_editor):
    QueryVQL = apps.get_model("Requests", "QueryVQL")
    file_path = "Requests/fixtures/artifacts.txt"

    artifact_name = None
    artifact_query = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("name:"):

                if artifact_name:
                    query_vql = "\n".join(artifact_query)
                    QueryVQL.objects.get_or_create(
                        name=artifact_name,
                        defaults={"query_vql": query_vql},
                    )


                artifact_name = line.split(":", 1)[1].strip()
                artifact_query = []

            else:
                artifact_query.append(line)


        if artifact_name:
            query_vql = "\n".join(artifact_query)
            QueryVQL.objects.get_or_create(
                name=artifact_name,
                defaults={"query_vql": query_vql},
            )

    except Exception as e:
        print(f"Ошибка загрузки артефактов: {e}")

def unload_artifacts(apps, schema_editor):
    QueryVQL = apps.get_model("Requests", "QueryVQL")
    file_path ="Requests/fixtures/artifacts.txt"

    artifact_name = None
    artifact_name_to_delete = []

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startwith("name:"):
                if artifact_name:
                    artifact_name_to_delete.append(artifact_name)
        if artifact_name:
            artifact_name_to_delete.append(artifact_name)

        QueryVQL.objects.filter(name__in=artifact_name_to_delete).delete()

    except Exception as e:
        print(f"Ошибка удаления: {e}")




class Migration(migrations.Migration):

    dependencies = [
        ('Requests', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_artifacts, unload_artifacts),
    ]
