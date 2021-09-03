# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: commu.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='commu.proto',
  package='commu',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0b\x63ommu.proto\x12\x05\x63ommu\"-\n\x07TaskReq\x12\x0f\n\x07task_id\x18\x01 \x01(\x05\x12\x11\n\tmember_id\x18\x02 \x01(\t\";\n\x0cMetadataResp\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x0f\n\x07\x64\x61taset\x18\x03 \x01(\t\"\x1d\n\nStatusResp\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\x1d\n\tRoundResp\x12\x10\n\x08round_id\x18\x01 \x01(\x05\";\n\x07\x46ileReq\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\x05\x12\x11\n\tmember_id\x18\x03 \x01(\t\"-\n\x08\x46ileResp\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\"c\n\tUploadReq\x12\x0f\n\x07task_id\x18\x01 \x01(\x05\x12\x11\n\tmember_id\x18\x02 \x01(\t\x12\x13\n\x0bupload_type\x18\x03 \x01(\t\x12\x0c\n\x04type\x18\x04 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x05 \x01(\x0c\"+\n\nUploadResp\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x32\xb6\x02\n\x05\x43ommu\x12\x34\n\x0bGetMetadata\x12\x0e.commu.TaskReq\x1a\x13.commu.MetadataResp\"\x00\x12/\n\x08JoinTask\x12\x0e.commu.TaskReq\x1a\x11.commu.StatusResp\"\x00\x12\x31\n\nFinishTask\x12\x0e.commu.TaskReq\x1a\x11.commu.StatusResp\"\x00\x12.\n\x08GetRound\x12\x0e.commu.TaskReq\x1a\x10.commu.RoundResp\"\x00\x12.\n\x07GetFile\x12\x0e.commu.FileReq\x1a\x0f.commu.FileResp\"\x00\x30\x01\x12\x33\n\x06Upload\x12\x10.commu.UploadReq\x1a\x11.commu.UploadResp\"\x00(\x01\x30\x01\x62\x06proto3'
)




_TASKREQ = _descriptor.Descriptor(
  name='TaskReq',
  full_name='commu.TaskReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='commu.TaskReq.task_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='member_id', full_name='commu.TaskReq.member_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=22,
  serialized_end=67,
)


_METADATARESP = _descriptor.Descriptor(
  name='MetadataResp',
  full_name='commu.MetadataResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='commu.MetadataResp.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='commu.MetadataResp.type', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dataset', full_name='commu.MetadataResp.dataset', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=69,
  serialized_end=128,
)


_STATUSRESP = _descriptor.Descriptor(
  name='StatusResp',
  full_name='commu.StatusResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='commu.StatusResp.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=130,
  serialized_end=159,
)


_ROUNDRESP = _descriptor.Descriptor(
  name='RoundResp',
  full_name='commu.RoundResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='round_id', full_name='commu.RoundResp.round_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=161,
  serialized_end=190,
)


_FILEREQ = _descriptor.Descriptor(
  name='FileReq',
  full_name='commu.FileReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='commu.FileReq.type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='task_id', full_name='commu.FileReq.task_id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='member_id', full_name='commu.FileReq.member_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=192,
  serialized_end=251,
)


_FILERESP = _descriptor.Descriptor(
  name='FileResp',
  full_name='commu.FileResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='filename', full_name='commu.FileResp.filename', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='content', full_name='commu.FileResp.content', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=253,
  serialized_end=298,
)


_UPLOADREQ = _descriptor.Descriptor(
  name='UploadReq',
  full_name='commu.UploadReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='commu.UploadReq.task_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='member_id', full_name='commu.UploadReq.member_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='upload_type', full_name='commu.UploadReq.upload_type', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='commu.UploadReq.type', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='content', full_name='commu.UploadReq.content', index=4,
      number=5, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=300,
  serialized_end=399,
)


_UPLOADRESP = _descriptor.Descriptor(
  name='UploadResp',
  full_name='commu.UploadResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='commu.UploadResp.type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='content', full_name='commu.UploadResp.content', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=401,
  serialized_end=444,
)

DESCRIPTOR.message_types_by_name['TaskReq'] = _TASKREQ
DESCRIPTOR.message_types_by_name['MetadataResp'] = _METADATARESP
DESCRIPTOR.message_types_by_name['StatusResp'] = _STATUSRESP
DESCRIPTOR.message_types_by_name['RoundResp'] = _ROUNDRESP
DESCRIPTOR.message_types_by_name['FileReq'] = _FILEREQ
DESCRIPTOR.message_types_by_name['FileResp'] = _FILERESP
DESCRIPTOR.message_types_by_name['UploadReq'] = _UPLOADREQ
DESCRIPTOR.message_types_by_name['UploadResp'] = _UPLOADRESP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TaskReq = _reflection.GeneratedProtocolMessageType('TaskReq', (_message.Message,), {
  'DESCRIPTOR' : _TASKREQ,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.TaskReq)
  })
_sym_db.RegisterMessage(TaskReq)

MetadataResp = _reflection.GeneratedProtocolMessageType('MetadataResp', (_message.Message,), {
  'DESCRIPTOR' : _METADATARESP,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.MetadataResp)
  })
_sym_db.RegisterMessage(MetadataResp)

StatusResp = _reflection.GeneratedProtocolMessageType('StatusResp', (_message.Message,), {
  'DESCRIPTOR' : _STATUSRESP,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.StatusResp)
  })
_sym_db.RegisterMessage(StatusResp)

RoundResp = _reflection.GeneratedProtocolMessageType('RoundResp', (_message.Message,), {
  'DESCRIPTOR' : _ROUNDRESP,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.RoundResp)
  })
_sym_db.RegisterMessage(RoundResp)

FileReq = _reflection.GeneratedProtocolMessageType('FileReq', (_message.Message,), {
  'DESCRIPTOR' : _FILEREQ,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.FileReq)
  })
_sym_db.RegisterMessage(FileReq)

FileResp = _reflection.GeneratedProtocolMessageType('FileResp', (_message.Message,), {
  'DESCRIPTOR' : _FILERESP,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.FileResp)
  })
_sym_db.RegisterMessage(FileResp)

UploadReq = _reflection.GeneratedProtocolMessageType('UploadReq', (_message.Message,), {
  'DESCRIPTOR' : _UPLOADREQ,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.UploadReq)
  })
_sym_db.RegisterMessage(UploadReq)

UploadResp = _reflection.GeneratedProtocolMessageType('UploadResp', (_message.Message,), {
  'DESCRIPTOR' : _UPLOADRESP,
  '__module__' : 'commu_pb2'
  # @@protoc_insertion_point(class_scope:commu.UploadResp)
  })
_sym_db.RegisterMessage(UploadResp)



_COMMU = _descriptor.ServiceDescriptor(
  name='Commu',
  full_name='commu.Commu',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=447,
  serialized_end=757,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetMetadata',
    full_name='commu.Commu.GetMetadata',
    index=0,
    containing_service=None,
    input_type=_TASKREQ,
    output_type=_METADATARESP,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='JoinTask',
    full_name='commu.Commu.JoinTask',
    index=1,
    containing_service=None,
    input_type=_TASKREQ,
    output_type=_STATUSRESP,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='FinishTask',
    full_name='commu.Commu.FinishTask',
    index=2,
    containing_service=None,
    input_type=_TASKREQ,
    output_type=_STATUSRESP,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetRound',
    full_name='commu.Commu.GetRound',
    index=3,
    containing_service=None,
    input_type=_TASKREQ,
    output_type=_ROUNDRESP,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetFile',
    full_name='commu.Commu.GetFile',
    index=4,
    containing_service=None,
    input_type=_FILEREQ,
    output_type=_FILERESP,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Upload',
    full_name='commu.Commu.Upload',
    index=5,
    containing_service=None,
    input_type=_UPLOADREQ,
    output_type=_UPLOADRESP,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_COMMU)

DESCRIPTOR.services_by_name['Commu'] = _COMMU

# @@protoc_insertion_point(module_scope)
