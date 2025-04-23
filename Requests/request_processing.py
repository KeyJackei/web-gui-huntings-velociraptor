from pyvelociraptor import api_pb2, api_pb2_grpc
import grpc
import json


#TODO: Вынести в класс
def request_processing(config, query, env_dict):
    print("----------requesting-----------")
    """Выполняет gRPC запрос и возвращает JSON-ответ."""
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8")
    )
    options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)
    env = [{"key": k, "value": v} for k, v in env_dict.items()]

    with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)
        request = api_pb2.VQLCollectorArgs(
            max_wait=1,
            max_row=100,
            Query=[api_pb2.VQLRequest(Name="Test", VQL=query)],
            env=env,
        )

        results = []
        for response in stub.Query(request):
            if response.Response:
                try:
                    package = json.loads(response.Response)
                    results.extend(package)
                except json.JSONDecodeError:
                    return {"error": "Ошибка: не удалось декодировать JSON"}
                except Exception as e:
                    return {"error": f"Ошибка: {str(e)}"}
        print(results)

        return results


def flatten_dict(data):
    """Рекурсивно преобразует вложенные словари и списки в удобочитаемый формат."""
    flat_data = {}

    for key, value in data.items():
        if isinstance(value, dict):
            # Рекурсивно разворачиваем вложенные словари
            nested_flat = flatten_dict(value)
            flat_data[key] = ", ".join(f"{k}: {v}" for k, v in nested_flat.items())
        elif isinstance(value, list):
            # Если в списке есть словари, тоже разворачиваем их
            flat_list = []
            for item in value:
                if isinstance(item, dict):
                    flat_list.append(", ".join(f"{k}: {v}" for k, v in flatten_dict(item).items()))
                else:
                    flat_list.append(str(item))
            flat_data[key] = "; ".join(flat_list)  # Используем ; как разделитель между объектами в списке
        else:
            flat_data[key] = value

    return flat_data


def generate_vql_query(client_id: str, artifact: str) -> str:
    print('---------------generate-----------------')
    return f"""
    LET collection <= collect_client(client_id='{client_id}', artifacts='{artifact}', env=dict())
    LET _ <= SELECT * FROM watch_monitoring(artifact='System.Flow.Completion') 
             WHERE FlowId = collection.flow_id LIMIT 1
    SELECT * FROM source(client_id=collection.request.client_id, flow_id=collection.flow_id, artifact='{artifact}')
    """.strip()
