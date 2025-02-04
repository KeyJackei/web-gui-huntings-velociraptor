from django.shortcuts import render

from .models import Artifact


def make_hunts(request):
    artifacts = Artifact.objects.all()
    return render(request, "make_hunts.html", {'artifact': artifacts})
