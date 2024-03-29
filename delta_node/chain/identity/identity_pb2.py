# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: identity.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ..transaction import transaction_pb2 as transaction__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eidentity.proto\x12\x08identity\x1a\x11transaction.proto\"$\n\x07JoinReq\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\",\n\x08JoinResp\x12\x0f\n\x07tx_hash\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\",\n\x0cUpdateUrlReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\".\n\rUpdateNameReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"\x1b\n\x08LeaveReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\"\x1e\n\x0bNodeInfoReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\"6\n\x08NodeInfo\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x03 \x01(\t\"/\n\x0cNodeInfosReq\x12\x0c\n\x04page\x18\x01 \x01(\x05\x12\x11\n\tpage_size\x18\x02 \x01(\x05\"C\n\tNodeInfos\x12!\n\x05nodes\x18\x01 \x03(\x0b\x32\x12.identity.NodeInfo\x12\x13\n\x0btotal_count\x18\x02 \x01(\x05\x32\xef\x02\n\x08Identity\x12/\n\x04Join\x12\x11.identity.JoinReq\x1a\x12.identity.JoinResp\"\x00\x12?\n\tUpdateUrl\x12\x16.identity.UpdateUrlReq\x1a\x18.transaction.Transaction\"\x00\x12\x41\n\nUpdateName\x12\x17.identity.UpdateNameReq\x1a\x18.transaction.Transaction\"\x00\x12\x37\n\x05Leave\x12\x12.identity.LeaveReq\x1a\x18.transaction.Transaction\"\x00\x12:\n\x0bGetNodeInfo\x12\x15.identity.NodeInfoReq\x1a\x12.identity.NodeInfo\"\x00\x12\x39\n\x08GetNodes\x12\x16.identity.NodeInfosReq\x1a\x13.identity.NodeInfos\"\x00\x62\x06proto3')



_JOINREQ = DESCRIPTOR.message_types_by_name['JoinReq']
_JOINRESP = DESCRIPTOR.message_types_by_name['JoinResp']
_UPDATEURLREQ = DESCRIPTOR.message_types_by_name['UpdateUrlReq']
_UPDATENAMEREQ = DESCRIPTOR.message_types_by_name['UpdateNameReq']
_LEAVEREQ = DESCRIPTOR.message_types_by_name['LeaveReq']
_NODEINFOREQ = DESCRIPTOR.message_types_by_name['NodeInfoReq']
_NODEINFO = DESCRIPTOR.message_types_by_name['NodeInfo']
_NODEINFOSREQ = DESCRIPTOR.message_types_by_name['NodeInfosReq']
_NODEINFOS = DESCRIPTOR.message_types_by_name['NodeInfos']
JoinReq = _reflection.GeneratedProtocolMessageType('JoinReq', (_message.Message,), {
  'DESCRIPTOR' : _JOINREQ,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.JoinReq)
  })
_sym_db.RegisterMessage(JoinReq)

JoinResp = _reflection.GeneratedProtocolMessageType('JoinResp', (_message.Message,), {
  'DESCRIPTOR' : _JOINRESP,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.JoinResp)
  })
_sym_db.RegisterMessage(JoinResp)

UpdateUrlReq = _reflection.GeneratedProtocolMessageType('UpdateUrlReq', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEURLREQ,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.UpdateUrlReq)
  })
_sym_db.RegisterMessage(UpdateUrlReq)

UpdateNameReq = _reflection.GeneratedProtocolMessageType('UpdateNameReq', (_message.Message,), {
  'DESCRIPTOR' : _UPDATENAMEREQ,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.UpdateNameReq)
  })
_sym_db.RegisterMessage(UpdateNameReq)

LeaveReq = _reflection.GeneratedProtocolMessageType('LeaveReq', (_message.Message,), {
  'DESCRIPTOR' : _LEAVEREQ,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.LeaveReq)
  })
_sym_db.RegisterMessage(LeaveReq)

NodeInfoReq = _reflection.GeneratedProtocolMessageType('NodeInfoReq', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFOREQ,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.NodeInfoReq)
  })
_sym_db.RegisterMessage(NodeInfoReq)

NodeInfo = _reflection.GeneratedProtocolMessageType('NodeInfo', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFO,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.NodeInfo)
  })
_sym_db.RegisterMessage(NodeInfo)

NodeInfosReq = _reflection.GeneratedProtocolMessageType('NodeInfosReq', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFOSREQ,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.NodeInfosReq)
  })
_sym_db.RegisterMessage(NodeInfosReq)

NodeInfos = _reflection.GeneratedProtocolMessageType('NodeInfos', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFOS,
  '__module__' : 'identity_pb2'
  # @@protoc_insertion_point(class_scope:identity.NodeInfos)
  })
_sym_db.RegisterMessage(NodeInfos)

_IDENTITY = DESCRIPTOR.services_by_name['Identity']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _JOINREQ._serialized_start=47
  _JOINREQ._serialized_end=83
  _JOINRESP._serialized_start=85
  _JOINRESP._serialized_end=129
  _UPDATEURLREQ._serialized_start=131
  _UPDATEURLREQ._serialized_end=175
  _UPDATENAMEREQ._serialized_start=177
  _UPDATENAMEREQ._serialized_end=223
  _LEAVEREQ._serialized_start=225
  _LEAVEREQ._serialized_end=252
  _NODEINFOREQ._serialized_start=254
  _NODEINFOREQ._serialized_end=284
  _NODEINFO._serialized_start=286
  _NODEINFO._serialized_end=340
  _NODEINFOSREQ._serialized_start=342
  _NODEINFOSREQ._serialized_end=389
  _NODEINFOS._serialized_start=391
  _NODEINFOS._serialized_end=458
  _IDENTITY._serialized_start=461
  _IDENTITY._serialized_end=828
# @@protoc_insertion_point(module_scope)
