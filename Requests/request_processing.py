from pyvelociraptor import api_pb2, api_pb2_grpc
import grpc
import json
from textwrap import dedent

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


def flatten_dict(data, parent_key='', sep='.'):
    """Преобразует вложенные словари в плоские с составными ключами."""
    flat_data = {}

    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            flat_data.update(flatten_dict(value, new_key, sep=sep))
        elif isinstance(value, list):
            items = []
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    flat_items = flatten_dict(item, f"{new_key}[{i}]", sep=sep)
                    flat_data.update(flat_items)
                else:
                    items.append(str(item))
            if items:
                flat_data[new_key] = "; ".join(items)
        else:
            flat_data[new_key] = value

    return flat_data


def generate_artifact_for_vql(query: str) -> str:
    """Генерирует VQL-запрос для временного артефакта"""
    # sanitized_query = query.replace('"', '\\"')
    return dedent(f"""
        SELECT artifact_set(definition='''name: Custom.Client.DynamicQuery
        type: CLIENT
        description: Шаблон для выполнения запросов из интерфейса
        parameters:
        - name: Command
          type: string
          default: {query}
        sources:
        - query: |
            SELECT * FROM query(query=Command, env=dict(config=config))''') FROM scope()
    """).strip()




def generate_vql_query(client_id: str, artifact: str) -> str:
    print('---------------generate-----------------')

    # Пользовательский артефакт
    if artifact == "Custom.Client.DynamicQuery":
        return dedent(f"""
            LET collection <= collect_client(
                client_id="{client_id}",
                artifacts="{artifact}"
            )

            LET _ <= SELECT * FROM watch_monitoring(artifact='System.Flow.Completion')
                     WHERE FlowId = collection.flow_id LIMIT 1

            SELECT * FROM source(
                client_id=collection.request.client_id,
                flow_id=collection.flow_id,
                artifact="{artifact}"
            )
        """).strip()

    # Артефакт из базы
    return dedent(f"""
        LET collection <= collect_client(
            client_id="{client_id}",
            artifacts="{artifact}",
            env=dict()
        )

        LET _ <= SELECT * FROM watch_monitoring(artifact='System.Flow.Completion') 
                 WHERE FlowId = collection.flow_id LIMIT 1

        SELECT * FROM source(
            client_id=collection.request.client_id,
            flow_id=collection.flow_id,
            artifact="{artifact}"
        )
    """).strip()
