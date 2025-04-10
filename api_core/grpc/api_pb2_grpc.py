# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import api_pb2 as api__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in api_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class APIStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Query = channel.unary_stream(
                '/proto.API/Query',
                request_serializer=api__pb2.VQLCollectorArgs.SerializeToString,
                response_deserializer=api__pb2.VQLResponse.FromString,
                _registered_method=True)
        self.VFSGetBuffer = channel.unary_unary(
                '/proto.API/VFSGetBuffer',
                request_serializer=api__pb2.VFSFileBuffer.SerializeToString,
                response_deserializer=api__pb2.VFSFileBuffer.FromString,
                _registered_method=True)
        self.WriteEvent = channel.unary_unary(
                '/proto.API/WriteEvent',
                request_serializer=api__pb2.VQLResponse.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.StartVQLFlow = channel.unary_unary(
                '/proto.API/StartVQLFlow',
                request_serializer=api__pb2.StartVQLFlowArgs.SerializeToString,
                response_deserializer=api__pb2.Flow.FromString,
                _registered_method=True)
        self.ListFlowResults = channel.unary_stream(
                '/proto.API/ListFlowResults',
                request_serializer=api__pb2.ListFlowResultsArgs.SerializeToString,
                response_deserializer=api__pb2.FlowResult.FromString,
                _registered_method=True)
        self.CreateFlow = channel.unary_unary(
                '/proto.API/CreateFlow',
                request_serializer=api__pb2.CreateFlowArgs.SerializeToString,
                response_deserializer=api__pb2.Flow.FromString,
                _registered_method=True)


class APIServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Query(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VFSGetBuffer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteEvent(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartVQLFlow(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListFlowResults(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateFlow(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_APIServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Query': grpc.unary_stream_rpc_method_handler(
                    servicer.Query,
                    request_deserializer=api__pb2.VQLCollectorArgs.FromString,
                    response_serializer=api__pb2.VQLResponse.SerializeToString,
            ),
            'VFSGetBuffer': grpc.unary_unary_rpc_method_handler(
                    servicer.VFSGetBuffer,
                    request_deserializer=api__pb2.VFSFileBuffer.FromString,
                    response_serializer=api__pb2.VFSFileBuffer.SerializeToString,
            ),
            'WriteEvent': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteEvent,
                    request_deserializer=api__pb2.VQLResponse.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'StartVQLFlow': grpc.unary_unary_rpc_method_handler(
                    servicer.StartVQLFlow,
                    request_deserializer=api__pb2.StartVQLFlowArgs.FromString,
                    response_serializer=api__pb2.Flow.SerializeToString,
            ),
            'ListFlowResults': grpc.unary_stream_rpc_method_handler(
                    servicer.ListFlowResults,
                    request_deserializer=api__pb2.ListFlowResultsArgs.FromString,
                    response_serializer=api__pb2.FlowResult.SerializeToString,
            ),
            'CreateFlow': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateFlow,
                    request_deserializer=api__pb2.CreateFlowArgs.FromString,
                    response_serializer=api__pb2.Flow.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'proto.API', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('proto.API', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class API(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Query(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/proto.API/Query',
            api__pb2.VQLCollectorArgs.SerializeToString,
            api__pb2.VQLResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def VFSGetBuffer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/proto.API/VFSGetBuffer',
            api__pb2.VFSFileBuffer.SerializeToString,
            api__pb2.VFSFileBuffer.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def WriteEvent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/proto.API/WriteEvent',
            api__pb2.VQLResponse.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StartVQLFlow(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/proto.API/StartVQLFlow',
            api__pb2.StartVQLFlowArgs.SerializeToString,
            api__pb2.Flow.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListFlowResults(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/proto.API/ListFlowResults',
            api__pb2.ListFlowResultsArgs.SerializeToString,
            api__pb2.FlowResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CreateFlow(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/proto.API/CreateFlow',
            api__pb2.CreateFlowArgs.SerializeToString,
            api__pb2.Flow.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
