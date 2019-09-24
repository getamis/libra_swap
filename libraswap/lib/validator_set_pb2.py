# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: validator_set.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import validator_public_keys_pb2 as validator__public__keys__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='validator_set.proto',
  package='types',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x13validator_set.proto\x12\x05types\x1a\x1bvalidator_public_keys.proto\"I\n\x0cValidatorSet\x12\x39\n\x15validator_public_keys\x18\x01 \x03(\x0b\x32\x1a.types.ValidatorPublicKeysb\x06proto3')
  ,
  dependencies=[validator__public__keys__pb2.DESCRIPTOR,])




_VALIDATORSET = _descriptor.Descriptor(
  name='ValidatorSet',
  full_name='types.ValidatorSet',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='validator_public_keys', full_name='types.ValidatorSet.validator_public_keys', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_start=59,
  serialized_end=132,
)

_VALIDATORSET.fields_by_name['validator_public_keys'].message_type = validator__public__keys__pb2._VALIDATORPUBLICKEYS
DESCRIPTOR.message_types_by_name['ValidatorSet'] = _VALIDATORSET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ValidatorSet = _reflection.GeneratedProtocolMessageType('ValidatorSet', (_message.Message,), {
  'DESCRIPTOR' : _VALIDATORSET,
  '__module__' : 'validator_set_pb2'
  # @@protoc_insertion_point(class_scope:types.ValidatorSet)
  })
_sym_db.RegisterMessage(ValidatorSet)


# @@protoc_insertion_point(module_scope)
