from django.http import JsonResponse
from django.shortcuts import render
import os
import yaml
from django.views.decorators.csrf import csrf_exempt
import json

from api_core.api_velociraptor import upload_artifacts
from .request_processing import request_processing, flatten_dict, generate_vql_query, generate_custom_vql_query
from .models import QueryVQL

ARTIFACT_YAML = f"""
name: Custom.Client.DynamicQuery
type: CLIENT
parameters:
- name: Query
  type: string
sources:
- query: |
    {{.Query}}
"""

def requests_page(request):
    artifacts = QueryVQL.objects.all()
    return render(request, 'requests.html', {'artifact': artifacts})

'''Представление для передачи запроса из командной строки'''
@csrf_exempt
def get_response(request):
    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()
        client_id = data.get("client_id")

        if not query:
            return JsonResponse({"success": False, "error": "Пустой запрос"})

        config_path = os.path.join(os.path.dirname('api_core/'), "api_keys/api-admin.config.yaml")
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        env_dict = {"Foo": "Bar"}
        query_cmd = generate_custom_vql_query(client_id, query)
        upload_artifacts(config, )
        results = request_processing(config, query_cmd, env_dict)

        parsed_results = [flatten_dict(item) for item in results]
        print('===generated===')
        return JsonResponse({"success": True, "results": parsed_results})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

def get_artifacts_description(request):
    name = request.GET.get('name')
    try:
        artifact = QueryVQL.objects.get(name=name)
        return JsonResponse({'query_vql': artifact.query_vql})
    except QueryVQL.DoesNotExist:
        return JsonResponse({'error': 'Артефакт не найден'})

@csrf_exempt
def run_artifact_view(request):
    try:
        data = json.loads(request.body)
        client_id = data.get("client_id")
        artifact = data.get("artifact")
        print(f"Получен запрос: client_id={client_id}, artifact={artifact}")
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Ошибка парсинга JSON: {str(e)}"})

    query = generate_vql_query(client_id, artifact)

    config_path = os.path.join(os.path.dirname("api_core/"), "api_keys/api-admin.config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    env_dict = {}
    raw_result = request_processing(config, query, env_dict)

    parsed_result = []

    for item in raw_result:
        if isinstance(item, dict):
            flat = flatten_dict(item)
            parsed_result.append(flat)
        else:
            parsed_result.append({"value": str(item)})

    # print("Результат выполнения запроса:", result)

    return JsonResponse({"success": True, "results": parsed_result})


