from django.http import JsonResponse
from django.shortcuts import render
import os
import yaml
from .request_processing import request_processing, flatten_dict


# Create your views here.
def requests_page(request):
    return render(request, 'requests.html')

def get_response(request):
    query = request.GET.get("query", "").strip()

    if not query:
        return JsonResponse({"success": False, "error": "Пустой запрос"})

    try:
        env_dict = {"Foo": "Bar"}
        config_path = os.path.join(os.path.dirname('api_core/'), "api_keys/api-admin.config.yaml")
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        results = request_processing(config, query, env_dict)

        # Обрабатываем каждый элемент списка через flatten_dict
        parsed_results = [flatten_dict(item) for item in results]
        print(parsed_results)

        return JsonResponse({"success": True, "results": parsed_results})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})