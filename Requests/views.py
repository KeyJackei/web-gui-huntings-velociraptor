from django.http import JsonResponse
from django.shortcuts import render
import os
import yaml
from django.views.decorators.csrf import csrf_exempt
import json

from .request_processing import request_processing, flatten_dict, generate_vql_query
from .models import QueryVQL


def requests_page(request):
    artifacts = QueryVQL.objects.all()
    return render(request, 'requests.html', {'artifact': artifacts})

# import pprint
#
# def get_response(request):
#     query = request.GET.get("query", "").strip()
#
#     if not query:
#         return JsonResponse({"success": False, "error": "Пустой запрос"})
#
#     try:
#         env_dict = {"Foo": "Bar"}
#         config_path = os.path.join(os.path.dirname('api_core/'), "api_keys/api-admin.config.yaml")
#         with open(config_path, 'r') as config_file:
#             config = yaml.safe_load(config_file)
#
#         results = request_processing(config, query, env_dict)
#
#         print("===== RAW RESULTS =====")
#         pprint.pprint(results, indent=2)
#
#         parsed_results = []
#         for item in results:
#             flat = flatten_dict(item)
#             print("===== FLATTENED ITEM =====")
#             pprint.pprint(flat, indent=2)
#             parsed_results.append(flat)
#
#         return JsonResponse({"success": True, "results": parsed_results})
#
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})

# def get_response(request):
#     query = request.GET.get("query", "").strip()
#
#     if not query:
#         return JsonResponse({"success": False, "error": "Пустой запрос"})
#
#     try:
#         env_dict = {"Foo": "Bar"}
#         config_path = os.path.join(os.path.dirname('api_core/'), "api_keys/api-admin.config.yaml")
#         with open(config_path, 'r') as config_file:
#             config = yaml.safe_load(config_file)
#
#         results = request_processing(config, query, env_dict)
#
#         parsed_results = [flatten_dict(item) for item in results]
#         # print(parsed_results)
#
#         return JsonResponse({"success": True, "results": parsed_results})
#
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})

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


