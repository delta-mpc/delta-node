# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chain.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x63hain.proto\x12\x05\x63hain\"\x1e\n\x0bTransaction\x12\x0f\n\x07tx_hash\x18\x01 \x01(\t\"$\n\x07JoinReq\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\",\n\x08JoinResp\x12\x0f\n\x07tx_hash\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\",\n\x0cUpdateUrlReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\".\n\rUpdateNameReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"\x1b\n\x08LeaveReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\"\x1e\n\x0bNodeInfoReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\"6\n\x08NodeInfo\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x03 \x01(\t\"/\n\x0cNodeInfosReq\x12\x0c\n\x04page\x18\x01 \x01(\x05\x12\x11\n\tpage_size\x18\x02 \x01(\x05\"@\n\tNodeInfos\x12\x1e\n\x05nodes\x18\x01 \x03(\x0b\x32\x0f.chain.NodeInfo\x12\x13\n\x0btotal_count\x18\x02 \x01(\x05\"X\n\rCreateTaskReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07\x64\x61taset\x18\x02 \x01(\t\x12\x12\n\ncommitment\x18\x03 \x01(\t\x12\x11\n\ttask_type\x18\x04 \x01(\t\"2\n\x0e\x43reateTaskResp\x12\x0f\n\x07tx_hash\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\"1\n\rFinishTaskReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\"\x1a\n\x07TaskReq\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"\x83\x01\n\x08TaskResp\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x12\x0f\n\x07task_id\x18\x03 \x01(\t\x12\x0f\n\x07\x64\x61taset\x18\x04 \x01(\t\x12\x12\n\ncommitment\x18\x05 \x01(\t\x12\x11\n\ttask_type\x18\x06 \x01(\t\x12\x10\n\x08\x66inished\x18\x07 \x01(\x08\"@\n\rStartRoundReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\"Y\n\x0cJoinRoundReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x0b\n\x03pk1\x18\x04 \x01(\t\x12\x0b\n\x03pk2\x18\x05 \x01(\t\".\n\x0cTaskRoundReq\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\"S\n\rTaskRoundResp\x12\r\n\x05round\x18\x01 \x01(\x05\x12\"\n\x06status\x18\x02 \x01(\x0e\x32\x12.chain.RoundStatus\x12\x0f\n\x07\x63lients\x18\x03 \x03(\t\"Q\n\rCandidatesReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x0f\n\x07\x63lients\x18\x04 \x03(\t\"j\n\x0fShareCommitment\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x11\n\treceivers\x18\x04 \x03(\t\x12\x13\n\x0b\x63ommitments\x18\x05 \x03(\t\"?\n\x0cPublicKeyReq\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\x12\x0f\n\x07\x63lients\x18\x03 \x03(\t\"&\n\nPublicKeys\x12\x0b\n\x03pk1\x18\x01 \x01(\t\x12\x0b\n\x03pk2\x18\x02 \x01(\t\"0\n\rPublicKeyResp\x12\x1f\n\x04keys\x18\x01 \x03(\x0b\x32\x11.chain.PublicKeys\"R\n\x0e\x43\x61lculationReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x0f\n\x07\x63lients\x18\x04 \x03(\t\"W\n\x10ResultCommitment\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x12\n\ncommitment\x18\x04 \x01(\t\"E\n\x13ResultCommitmentReq\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\x12\x0e\n\x06\x63lient\x18\x03 \x01(\t\"*\n\x14ResultCommitmentResp\x12\x12\n\ncommitment\x18\x01 \x01(\t\"R\n\x0e\x41ggregationReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x0f\n\x07\x63lients\x18\x04 \x03(\t\"Y\n\x05Share\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\x12\x0f\n\x07senders\x18\x04 \x03(\t\x12\x0e\n\x06shares\x18\x05 \x03(\t\"S\n\x0eSecretShareReq\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\x12\x0f\n\x07senders\x18\x03 \x03(\t\x12\x10\n\x08receiver\x18\x04 \x01(\t\"\xc5\x01\n\x0fSecretShareData\x12\x11\n\x04seed\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x1c\n\x0fseed_commitment\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\nsecret_key\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\"\n\x15secret_key_commitment\x18\x04 \x01(\tH\x03\x88\x01\x01\x42\x07\n\x05_seedB\x12\n\x10_seed_commitmentB\r\n\x0b_secret_keyB\x18\n\x16_secret_key_commitment\"9\n\x0fSecretShareResp\x12&\n\x06shares\x18\x01 \x03(\x0b\x32\x16.chain.SecretShareData\">\n\x0b\x45ndRoundReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\r\n\x05round\x18\x03 \x01(\x05\",\n\x08\x45ventReq\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07timeout\x18\x02 \x01(\x05\"\xb6\x03\n\x05\x45vent\x12.\n\x0ctask_created\x18\x01 \x01(\x0b\x32\x16.chain.TaskCreateEventH\x00\x12\x31\n\rround_started\x18\x02 \x01(\x0b\x32\x18.chain.RoundStartedEventH\x00\x12\x37\n\x10partner_selected\x18\x03 \x01(\x0b\x32\x1b.chain.PartnerSelectedEventH\x00\x12=\n\x13\x63\x61lculation_started\x18\x04 \x01(\x0b\x32\x1e.chain.CalculationStartedEventH\x00\x12=\n\x13\x61ggregation_started\x18\x05 \x01(\x0b\x32\x1e.chain.AggregationStartedEventH\x00\x12-\n\x0bround_ended\x18\x06 \x01(\x0b\x32\x16.chain.RoundEndedEventH\x00\x12/\n\rtask_finished\x18\x07 \x01(\x0b\x32\x16.chain.TaskFinishEventH\x00\x12*\n\theartbeat\x18\x08 \x01(\x0b\x32\x15.chain.HeartBeatEventH\x00\x42\x07\n\x05\x65vent\"x\n\x0fTaskCreateEvent\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\x0f\n\x07\x64\x61taset\x18\x03 \x01(\t\x12\x0b\n\x03url\x18\x04 \x01(\t\x12\x12\n\ncommitment\x18\x05 \x01(\t\x12\x11\n\ttask_type\x18\x06 \x01(\t\"3\n\x11RoundStartedEvent\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\"E\n\x14PartnerSelectedEvent\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\x12\r\n\x05\x61\x64\x64rs\x18\x03 \x03(\t\"H\n\x17\x43\x61lculationStartedEvent\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\x12\r\n\x05\x61\x64\x64rs\x18\x03 \x03(\t\"H\n\x17\x41ggregationStartedEvent\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\x12\r\n\x05\x61\x64\x64rs\x18\x03 \x03(\t\"1\n\x0fRoundEndedEvent\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\r\n\x05round\x18\x02 \x01(\x05\"\"\n\x0fTaskFinishEvent\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"\x10\n\x0eHeartBeatEvent*W\n\x0bRoundStatus\x12\x0b\n\x07STARTED\x10\x00\x12\x0b\n\x07RUNNING\x10\x01\x12\x0f\n\x0b\x43\x41LCULATING\x10\x02\x12\x0f\n\x0b\x41GGREGATING\x10\x03\x12\x0c\n\x08\x46INISHED\x10\x04\x32\xdd\x0b\n\x05\x43hain\x12)\n\x04Join\x12\x0e.chain.JoinReq\x1a\x0f.chain.JoinResp\"\x00\x12\x36\n\tUpdateUrl\x12\x13.chain.UpdateUrlReq\x1a\x12.chain.Transaction\"\x00\x12\x38\n\nUpdateName\x12\x14.chain.UpdateNameReq\x1a\x12.chain.Transaction\"\x00\x12.\n\x05Leave\x12\x0f.chain.LeaveReq\x1a\x12.chain.Transaction\"\x00\x12\x34\n\x0bGetNodeInfo\x12\x12.chain.NodeInfoReq\x1a\x0f.chain.NodeInfo\"\x00\x12\x33\n\x08GetNodes\x12\x13.chain.NodeInfosReq\x1a\x10.chain.NodeInfos\"\x00\x12;\n\nCreateTask\x12\x14.chain.CreateTaskReq\x1a\x15.chain.CreateTaskResp\"\x00\x12\x38\n\nFinishTask\x12\x14.chain.FinishTaskReq\x1a\x12.chain.Transaction\"\x00\x12,\n\x07GetTask\x12\x0e.chain.TaskReq\x1a\x0f.chain.TaskResp\"\x00\x12\x38\n\nStartRound\x12\x14.chain.StartRoundReq\x1a\x12.chain.Transaction\"\x00\x12\x36\n\tJoinRound\x12\x13.chain.JoinRoundReq\x1a\x12.chain.Transaction\"\x00\x12;\n\x0cGetTaskRound\x12\x13.chain.TaskRoundReq\x1a\x14.chain.TaskRoundResp\"\x00\x12>\n\x10SelectCandidates\x12\x14.chain.CandidatesReq\x1a\x12.chain.Transaction\"\x00\x12\x44\n\x14UploadSeedCommitment\x12\x16.chain.ShareCommitment\x1a\x12.chain.Transaction\"\x00\x12I\n\x19UploadSecretKeyCommitment\x12\x16.chain.ShareCommitment\x1a\x12.chain.Transaction\"\x00\x12\x43\n\x14GetClientPublickKeys\x12\x13.chain.PublicKeyReq\x1a\x14.chain.PublicKeyResp\"\x00\x12?\n\x10StartCalculation\x12\x15.chain.CalculationReq\x1a\x12.chain.Transaction\"\x00\x12G\n\x16UploadResultCommitment\x12\x17.chain.ResultCommitment\x1a\x12.chain.Transaction\"\x00\x12P\n\x13GetResultCommitment\x12\x1a.chain.ResultCommitmentReq\x1a\x1b.chain.ResultCommitmentResp\"\x00\x12?\n\x10StartAggregation\x12\x15.chain.AggregationReq\x1a\x12.chain.Transaction\"\x00\x12\x30\n\nUploadSeed\x12\x0c.chain.Share\x1a\x12.chain.Transaction\"\x00\x12\x35\n\x0fUploadSecretKey\x12\x0c.chain.Share\x1a\x12.chain.Transaction\"\x00\x12\x46\n\x13GetSecretShareDatas\x12\x15.chain.SecretShareReq\x1a\x16.chain.SecretShareResp\"\x00\x12\x34\n\x08\x45ndRound\x12\x12.chain.EndRoundReq\x1a\x12.chain.Transaction\"\x00\x12.\n\tSubscribe\x12\x0f.chain.EventReq\x1a\x0c.chain.Event\"\x00\x30\x01\x62\x06proto3')

_ROUNDSTATUS = DESCRIPTOR.enum_types_by_name['RoundStatus']
RoundStatus = enum_type_wrapper.EnumTypeWrapper(_ROUNDSTATUS)
STARTED = 0
RUNNING = 1
CALCULATING = 2
AGGREGATING = 3
FINISHED = 4


_TRANSACTION = DESCRIPTOR.message_types_by_name['Transaction']
_JOINREQ = DESCRIPTOR.message_types_by_name['JoinReq']
_JOINRESP = DESCRIPTOR.message_types_by_name['JoinResp']
_UPDATEURLREQ = DESCRIPTOR.message_types_by_name['UpdateUrlReq']
_UPDATENAMEREQ = DESCRIPTOR.message_types_by_name['UpdateNameReq']
_LEAVEREQ = DESCRIPTOR.message_types_by_name['LeaveReq']
_NODEINFOREQ = DESCRIPTOR.message_types_by_name['NodeInfoReq']
_NODEINFO = DESCRIPTOR.message_types_by_name['NodeInfo']
_NODEINFOSREQ = DESCRIPTOR.message_types_by_name['NodeInfosReq']
_NODEINFOS = DESCRIPTOR.message_types_by_name['NodeInfos']
_CREATETASKREQ = DESCRIPTOR.message_types_by_name['CreateTaskReq']
_CREATETASKRESP = DESCRIPTOR.message_types_by_name['CreateTaskResp']
_FINISHTASKREQ = DESCRIPTOR.message_types_by_name['FinishTaskReq']
_TASKREQ = DESCRIPTOR.message_types_by_name['TaskReq']
_TASKRESP = DESCRIPTOR.message_types_by_name['TaskResp']
_STARTROUNDREQ = DESCRIPTOR.message_types_by_name['StartRoundReq']
_JOINROUNDREQ = DESCRIPTOR.message_types_by_name['JoinRoundReq']
_TASKROUNDREQ = DESCRIPTOR.message_types_by_name['TaskRoundReq']
_TASKROUNDRESP = DESCRIPTOR.message_types_by_name['TaskRoundResp']
_CANDIDATESREQ = DESCRIPTOR.message_types_by_name['CandidatesReq']
_SHARECOMMITMENT = DESCRIPTOR.message_types_by_name['ShareCommitment']
_PUBLICKEYREQ = DESCRIPTOR.message_types_by_name['PublicKeyReq']
_PUBLICKEYS = DESCRIPTOR.message_types_by_name['PublicKeys']
_PUBLICKEYRESP = DESCRIPTOR.message_types_by_name['PublicKeyResp']
_CALCULATIONREQ = DESCRIPTOR.message_types_by_name['CalculationReq']
_RESULTCOMMITMENT = DESCRIPTOR.message_types_by_name['ResultCommitment']
_RESULTCOMMITMENTREQ = DESCRIPTOR.message_types_by_name['ResultCommitmentReq']
_RESULTCOMMITMENTRESP = DESCRIPTOR.message_types_by_name['ResultCommitmentResp']
_AGGREGATIONREQ = DESCRIPTOR.message_types_by_name['AggregationReq']
_SHARE = DESCRIPTOR.message_types_by_name['Share']
_SECRETSHAREREQ = DESCRIPTOR.message_types_by_name['SecretShareReq']
_SECRETSHAREDATA = DESCRIPTOR.message_types_by_name['SecretShareData']
_SECRETSHARERESP = DESCRIPTOR.message_types_by_name['SecretShareResp']
_ENDROUNDREQ = DESCRIPTOR.message_types_by_name['EndRoundReq']
_EVENTREQ = DESCRIPTOR.message_types_by_name['EventReq']
_EVENT = DESCRIPTOR.message_types_by_name['Event']
_TASKCREATEEVENT = DESCRIPTOR.message_types_by_name['TaskCreateEvent']
_ROUNDSTARTEDEVENT = DESCRIPTOR.message_types_by_name['RoundStartedEvent']
_PARTNERSELECTEDEVENT = DESCRIPTOR.message_types_by_name['PartnerSelectedEvent']
_CALCULATIONSTARTEDEVENT = DESCRIPTOR.message_types_by_name['CalculationStartedEvent']
_AGGREGATIONSTARTEDEVENT = DESCRIPTOR.message_types_by_name['AggregationStartedEvent']
_ROUNDENDEDEVENT = DESCRIPTOR.message_types_by_name['RoundEndedEvent']
_TASKFINISHEVENT = DESCRIPTOR.message_types_by_name['TaskFinishEvent']
_HEARTBEATEVENT = DESCRIPTOR.message_types_by_name['HeartBeatEvent']
Transaction = _reflection.GeneratedProtocolMessageType('Transaction', (_message.Message,), {
  'DESCRIPTOR' : _TRANSACTION,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.Transaction)
  })
_sym_db.RegisterMessage(Transaction)

JoinReq = _reflection.GeneratedProtocolMessageType('JoinReq', (_message.Message,), {
  'DESCRIPTOR' : _JOINREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.JoinReq)
  })
_sym_db.RegisterMessage(JoinReq)

JoinResp = _reflection.GeneratedProtocolMessageType('JoinResp', (_message.Message,), {
  'DESCRIPTOR' : _JOINRESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.JoinResp)
  })
_sym_db.RegisterMessage(JoinResp)

UpdateUrlReq = _reflection.GeneratedProtocolMessageType('UpdateUrlReq', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEURLREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.UpdateUrlReq)
  })
_sym_db.RegisterMessage(UpdateUrlReq)

UpdateNameReq = _reflection.GeneratedProtocolMessageType('UpdateNameReq', (_message.Message,), {
  'DESCRIPTOR' : _UPDATENAMEREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.UpdateNameReq)
  })
_sym_db.RegisterMessage(UpdateNameReq)

LeaveReq = _reflection.GeneratedProtocolMessageType('LeaveReq', (_message.Message,), {
  'DESCRIPTOR' : _LEAVEREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.LeaveReq)
  })
_sym_db.RegisterMessage(LeaveReq)

NodeInfoReq = _reflection.GeneratedProtocolMessageType('NodeInfoReq', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFOREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.NodeInfoReq)
  })
_sym_db.RegisterMessage(NodeInfoReq)

NodeInfo = _reflection.GeneratedProtocolMessageType('NodeInfo', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFO,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.NodeInfo)
  })
_sym_db.RegisterMessage(NodeInfo)

NodeInfosReq = _reflection.GeneratedProtocolMessageType('NodeInfosReq', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFOSREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.NodeInfosReq)
  })
_sym_db.RegisterMessage(NodeInfosReq)

NodeInfos = _reflection.GeneratedProtocolMessageType('NodeInfos', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFOS,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.NodeInfos)
  })
_sym_db.RegisterMessage(NodeInfos)

CreateTaskReq = _reflection.GeneratedProtocolMessageType('CreateTaskReq', (_message.Message,), {
  'DESCRIPTOR' : _CREATETASKREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.CreateTaskReq)
  })
_sym_db.RegisterMessage(CreateTaskReq)

CreateTaskResp = _reflection.GeneratedProtocolMessageType('CreateTaskResp', (_message.Message,), {
  'DESCRIPTOR' : _CREATETASKRESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.CreateTaskResp)
  })
_sym_db.RegisterMessage(CreateTaskResp)

FinishTaskReq = _reflection.GeneratedProtocolMessageType('FinishTaskReq', (_message.Message,), {
  'DESCRIPTOR' : _FINISHTASKREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.FinishTaskReq)
  })
_sym_db.RegisterMessage(FinishTaskReq)

TaskReq = _reflection.GeneratedProtocolMessageType('TaskReq', (_message.Message,), {
  'DESCRIPTOR' : _TASKREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.TaskReq)
  })
_sym_db.RegisterMessage(TaskReq)

TaskResp = _reflection.GeneratedProtocolMessageType('TaskResp', (_message.Message,), {
  'DESCRIPTOR' : _TASKRESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.TaskResp)
  })
_sym_db.RegisterMessage(TaskResp)

StartRoundReq = _reflection.GeneratedProtocolMessageType('StartRoundReq', (_message.Message,), {
  'DESCRIPTOR' : _STARTROUNDREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.StartRoundReq)
  })
_sym_db.RegisterMessage(StartRoundReq)

JoinRoundReq = _reflection.GeneratedProtocolMessageType('JoinRoundReq', (_message.Message,), {
  'DESCRIPTOR' : _JOINROUNDREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.JoinRoundReq)
  })
_sym_db.RegisterMessage(JoinRoundReq)

TaskRoundReq = _reflection.GeneratedProtocolMessageType('TaskRoundReq', (_message.Message,), {
  'DESCRIPTOR' : _TASKROUNDREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.TaskRoundReq)
  })
_sym_db.RegisterMessage(TaskRoundReq)

TaskRoundResp = _reflection.GeneratedProtocolMessageType('TaskRoundResp', (_message.Message,), {
  'DESCRIPTOR' : _TASKROUNDRESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.TaskRoundResp)
  })
_sym_db.RegisterMessage(TaskRoundResp)

CandidatesReq = _reflection.GeneratedProtocolMessageType('CandidatesReq', (_message.Message,), {
  'DESCRIPTOR' : _CANDIDATESREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.CandidatesReq)
  })
_sym_db.RegisterMessage(CandidatesReq)

ShareCommitment = _reflection.GeneratedProtocolMessageType('ShareCommitment', (_message.Message,), {
  'DESCRIPTOR' : _SHARECOMMITMENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.ShareCommitment)
  })
_sym_db.RegisterMessage(ShareCommitment)

PublicKeyReq = _reflection.GeneratedProtocolMessageType('PublicKeyReq', (_message.Message,), {
  'DESCRIPTOR' : _PUBLICKEYREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.PublicKeyReq)
  })
_sym_db.RegisterMessage(PublicKeyReq)

PublicKeys = _reflection.GeneratedProtocolMessageType('PublicKeys', (_message.Message,), {
  'DESCRIPTOR' : _PUBLICKEYS,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.PublicKeys)
  })
_sym_db.RegisterMessage(PublicKeys)

PublicKeyResp = _reflection.GeneratedProtocolMessageType('PublicKeyResp', (_message.Message,), {
  'DESCRIPTOR' : _PUBLICKEYRESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.PublicKeyResp)
  })
_sym_db.RegisterMessage(PublicKeyResp)

CalculationReq = _reflection.GeneratedProtocolMessageType('CalculationReq', (_message.Message,), {
  'DESCRIPTOR' : _CALCULATIONREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.CalculationReq)
  })
_sym_db.RegisterMessage(CalculationReq)

ResultCommitment = _reflection.GeneratedProtocolMessageType('ResultCommitment', (_message.Message,), {
  'DESCRIPTOR' : _RESULTCOMMITMENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.ResultCommitment)
  })
_sym_db.RegisterMessage(ResultCommitment)

ResultCommitmentReq = _reflection.GeneratedProtocolMessageType('ResultCommitmentReq', (_message.Message,), {
  'DESCRIPTOR' : _RESULTCOMMITMENTREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.ResultCommitmentReq)
  })
_sym_db.RegisterMessage(ResultCommitmentReq)

ResultCommitmentResp = _reflection.GeneratedProtocolMessageType('ResultCommitmentResp', (_message.Message,), {
  'DESCRIPTOR' : _RESULTCOMMITMENTRESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.ResultCommitmentResp)
  })
_sym_db.RegisterMessage(ResultCommitmentResp)

AggregationReq = _reflection.GeneratedProtocolMessageType('AggregationReq', (_message.Message,), {
  'DESCRIPTOR' : _AGGREGATIONREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.AggregationReq)
  })
_sym_db.RegisterMessage(AggregationReq)

Share = _reflection.GeneratedProtocolMessageType('Share', (_message.Message,), {
  'DESCRIPTOR' : _SHARE,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.Share)
  })
_sym_db.RegisterMessage(Share)

SecretShareReq = _reflection.GeneratedProtocolMessageType('SecretShareReq', (_message.Message,), {
  'DESCRIPTOR' : _SECRETSHAREREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.SecretShareReq)
  })
_sym_db.RegisterMessage(SecretShareReq)

SecretShareData = _reflection.GeneratedProtocolMessageType('SecretShareData', (_message.Message,), {
  'DESCRIPTOR' : _SECRETSHAREDATA,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.SecretShareData)
  })
_sym_db.RegisterMessage(SecretShareData)

SecretShareResp = _reflection.GeneratedProtocolMessageType('SecretShareResp', (_message.Message,), {
  'DESCRIPTOR' : _SECRETSHARERESP,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.SecretShareResp)
  })
_sym_db.RegisterMessage(SecretShareResp)

EndRoundReq = _reflection.GeneratedProtocolMessageType('EndRoundReq', (_message.Message,), {
  'DESCRIPTOR' : _ENDROUNDREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.EndRoundReq)
  })
_sym_db.RegisterMessage(EndRoundReq)

EventReq = _reflection.GeneratedProtocolMessageType('EventReq', (_message.Message,), {
  'DESCRIPTOR' : _EVENTREQ,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.EventReq)
  })
_sym_db.RegisterMessage(EventReq)

Event = _reflection.GeneratedProtocolMessageType('Event', (_message.Message,), {
  'DESCRIPTOR' : _EVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.Event)
  })
_sym_db.RegisterMessage(Event)

TaskCreateEvent = _reflection.GeneratedProtocolMessageType('TaskCreateEvent', (_message.Message,), {
  'DESCRIPTOR' : _TASKCREATEEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.TaskCreateEvent)
  })
_sym_db.RegisterMessage(TaskCreateEvent)

RoundStartedEvent = _reflection.GeneratedProtocolMessageType('RoundStartedEvent', (_message.Message,), {
  'DESCRIPTOR' : _ROUNDSTARTEDEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.RoundStartedEvent)
  })
_sym_db.RegisterMessage(RoundStartedEvent)

PartnerSelectedEvent = _reflection.GeneratedProtocolMessageType('PartnerSelectedEvent', (_message.Message,), {
  'DESCRIPTOR' : _PARTNERSELECTEDEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.PartnerSelectedEvent)
  })
_sym_db.RegisterMessage(PartnerSelectedEvent)

CalculationStartedEvent = _reflection.GeneratedProtocolMessageType('CalculationStartedEvent', (_message.Message,), {
  'DESCRIPTOR' : _CALCULATIONSTARTEDEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.CalculationStartedEvent)
  })
_sym_db.RegisterMessage(CalculationStartedEvent)

AggregationStartedEvent = _reflection.GeneratedProtocolMessageType('AggregationStartedEvent', (_message.Message,), {
  'DESCRIPTOR' : _AGGREGATIONSTARTEDEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.AggregationStartedEvent)
  })
_sym_db.RegisterMessage(AggregationStartedEvent)

RoundEndedEvent = _reflection.GeneratedProtocolMessageType('RoundEndedEvent', (_message.Message,), {
  'DESCRIPTOR' : _ROUNDENDEDEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.RoundEndedEvent)
  })
_sym_db.RegisterMessage(RoundEndedEvent)

TaskFinishEvent = _reflection.GeneratedProtocolMessageType('TaskFinishEvent', (_message.Message,), {
  'DESCRIPTOR' : _TASKFINISHEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.TaskFinishEvent)
  })
_sym_db.RegisterMessage(TaskFinishEvent)

HeartBeatEvent = _reflection.GeneratedProtocolMessageType('HeartBeatEvent', (_message.Message,), {
  'DESCRIPTOR' : _HEARTBEATEVENT,
  '__module__' : 'chain_pb2'
  # @@protoc_insertion_point(class_scope:chain.HeartBeatEvent)
  })
_sym_db.RegisterMessage(HeartBeatEvent)

_CHAIN = DESCRIPTOR.services_by_name['Chain']
if _descriptor._USE_C_DESCRIPTORS == False:  # type: ignore

  DESCRIPTOR._options = None
  _ROUNDSTATUS._serialized_start=3312
  _ROUNDSTATUS._serialized_end=3399
  _TRANSACTION._serialized_start=22
  _TRANSACTION._serialized_end=52
  _JOINREQ._serialized_start=54
  _JOINREQ._serialized_end=90
  _JOINRESP._serialized_start=92
  _JOINRESP._serialized_end=136
  _UPDATEURLREQ._serialized_start=138
  _UPDATEURLREQ._serialized_end=182
  _UPDATENAMEREQ._serialized_start=184
  _UPDATENAMEREQ._serialized_end=230
  _LEAVEREQ._serialized_start=232
  _LEAVEREQ._serialized_end=259
  _NODEINFOREQ._serialized_start=261
  _NODEINFOREQ._serialized_end=291
  _NODEINFO._serialized_start=293
  _NODEINFO._serialized_end=347
  _NODEINFOSREQ._serialized_start=349
  _NODEINFOSREQ._serialized_end=396
  _NODEINFOS._serialized_start=398
  _NODEINFOS._serialized_end=462
  _CREATETASKREQ._serialized_start=464
  _CREATETASKREQ._serialized_end=552
  _CREATETASKRESP._serialized_start=554
  _CREATETASKRESP._serialized_end=604
  _FINISHTASKREQ._serialized_start=606
  _FINISHTASKREQ._serialized_end=655
  _TASKREQ._serialized_start=657
  _TASKREQ._serialized_end=683
  _TASKRESP._serialized_start=686
  _TASKRESP._serialized_end=817
  _STARTROUNDREQ._serialized_start=819
  _STARTROUNDREQ._serialized_end=883
  _JOINROUNDREQ._serialized_start=885
  _JOINROUNDREQ._serialized_end=974
  _TASKROUNDREQ._serialized_start=976
  _TASKROUNDREQ._serialized_end=1022
  _TASKROUNDRESP._serialized_start=1024
  _TASKROUNDRESP._serialized_end=1107
  _CANDIDATESREQ._serialized_start=1109
  _CANDIDATESREQ._serialized_end=1190
  _SHARECOMMITMENT._serialized_start=1192
  _SHARECOMMITMENT._serialized_end=1298
  _PUBLICKEYREQ._serialized_start=1300
  _PUBLICKEYREQ._serialized_end=1363
  _PUBLICKEYS._serialized_start=1365
  _PUBLICKEYS._serialized_end=1403
  _PUBLICKEYRESP._serialized_start=1405
  _PUBLICKEYRESP._serialized_end=1453
  _CALCULATIONREQ._serialized_start=1455
  _CALCULATIONREQ._serialized_end=1537
  _RESULTCOMMITMENT._serialized_start=1539
  _RESULTCOMMITMENT._serialized_end=1626
  _RESULTCOMMITMENTREQ._serialized_start=1628
  _RESULTCOMMITMENTREQ._serialized_end=1697
  _RESULTCOMMITMENTRESP._serialized_start=1699
  _RESULTCOMMITMENTRESP._serialized_end=1741
  _AGGREGATIONREQ._serialized_start=1743
  _AGGREGATIONREQ._serialized_end=1825
  _SHARE._serialized_start=1827
  _SHARE._serialized_end=1916
  _SECRETSHAREREQ._serialized_start=1918
  _SECRETSHAREREQ._serialized_end=2001
  _SECRETSHAREDATA._serialized_start=2004
  _SECRETSHAREDATA._serialized_end=2201
  _SECRETSHARERESP._serialized_start=2203
  _SECRETSHARERESP._serialized_end=2260
  _ENDROUNDREQ._serialized_start=2262
  _ENDROUNDREQ._serialized_end=2324
  _EVENTREQ._serialized_start=2326
  _EVENTREQ._serialized_end=2370
  _EVENT._serialized_start=2373
  _EVENT._serialized_end=2811
  _TASKCREATEEVENT._serialized_start=2813
  _TASKCREATEEVENT._serialized_end=2933
  _ROUNDSTARTEDEVENT._serialized_start=2935
  _ROUNDSTARTEDEVENT._serialized_end=2986
  _PARTNERSELECTEDEVENT._serialized_start=2988
  _PARTNERSELECTEDEVENT._serialized_end=3057
  _CALCULATIONSTARTEDEVENT._serialized_start=3059
  _CALCULATIONSTARTEDEVENT._serialized_end=3131
  _AGGREGATIONSTARTEDEVENT._serialized_start=3133
  _AGGREGATIONSTARTEDEVENT._serialized_end=3205
  _ROUNDENDEDEVENT._serialized_start=3207
  _ROUNDENDEDEVENT._serialized_end=3256
  _TASKFINISHEVENT._serialized_start=3258
  _TASKFINISHEVENT._serialized_end=3292
  _HEARTBEATEVENT._serialized_start=3294
  _HEARTBEATEVENT._serialized_end=3310
  _CHAIN._serialized_start=3402
  _CHAIN._serialized_end=4903
# @@protoc_insertion_point(module_scope)
