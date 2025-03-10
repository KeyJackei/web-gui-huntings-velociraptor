from django.http import JsonResponse
from django.shortcuts import render

from .models import QueryVQL


def make_hunts(request):
    artifacts = QueryVQL.objects.all()
    return render(request, "make_hunts.html", {'artifact': artifacts})

def get_artifact(request, name):
    try:
        artifact = QueryVQL.objects.get(name=name)
        return JsonResponse({'query_vql': artifact.query_vql})
    except QueryVQL.DoesNotExist:
        return JsonResponse({'error': 'Артефакт не найден'}, status=404)