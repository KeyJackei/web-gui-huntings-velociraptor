from django.shortcuts import render

from .models import QueryVQL


def make_hunts(request):
    artifacts = QueryVQL.objects.all()
    return render(request, "make_hunts.html", {'artifact': artifacts})

def get_query_by_name(name):
    try:
        record = QueryVQL.objects.get(name=name)
        return record.query_vql
    except QueryVQL.DoesNotExist:
        return None
