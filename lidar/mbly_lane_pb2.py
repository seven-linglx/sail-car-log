# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


DESCRIPTOR = descriptor.FileDescriptor(
  name='mbly_lane.proto',
  package='mbly',
  serialized_pb='\n\x0fmbly_lane.proto\x12\x04mbly\"\xd5\x04\n\x04Lane\x12\x11\n\ttimestamp\x18\x01 \x01(\x04\x12\x0f\n\x07lane_id\x18\x02 \x01(\x05\x12\n\n\x02\x43\x30\x18\x03 \x01(\x02\x12\n\n\x02\x43\x31\x18\x04 \x01(\x02\x12\n\n\x02\x43\x32\x18\x05 \x01(\x02\x12\n\n\x02\x43\x33\x18\x06 \x01(\x02\x12\"\n\tlane_type\x18\x07 \x01(\x0e\x32\x0f.mbly.Lane.Type\x12-\n\x0cmodel_degree\x18\x08 \x01(\x0e\x32\x17.mbly.Lane.Model_Degree\x12#\n\x07quality\x18\t \x01(\x0e\x32\x12.mbly.Lane.Quality\x12\x43\n\x17view_range_availability\x18\n \x01(\x0e\x32\".mbly.Lane.View_Range_Availibility\x12\x12\n\nview_range\x18\x0b \x01(\x02\"d\n\x04Type\x12\n\n\x06\x44\x61shed\x10\x00\x12\t\n\x05Solid\x10\x01\x12\r\n\tundecided\x10\x02\x12\r\n\tRoad_Edge\x10\x03\x12\n\n\x06\x44ouble\x10\x04\x12\x0e\n\nBotts_Dots\x10\x05\x12\x0b\n\x07Invalid\x10\x06\"4\n\x0cModel_Degree\x12\n\n\x06Linear\x10\x01\x12\r\n\tParabolic\x10\x02\x12\t\n\x05\x43ubic\x10\x03\"W\n\x07Quality\x12\x11\n\rLow_Quality_0\x10\x00\x12\x11\n\rLow_Quality_1\x10\x01\x12\x12\n\x0eHigh_Quality_2\x10\x02\x12\x12\n\x0eHigh_Quality_3\x10\x03\"3\n\x17View_Range_Availibility\x12\r\n\tNot_Valid\x10\x00\x12\t\n\x05Valid\x10\x01\"!\n\x05Lanes\x12\x18\n\x04lane\x18\x01 \x03(\x0b\x32\n.mbly.Lane')



_LANE_TYPE = descriptor.EnumDescriptor(
  name='Type',
  full_name='mbly.Lane.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='Dashed', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Solid', index=1, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='undecided', index=2, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Road_Edge', index=3, number=3,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Double', index=4, number=4,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Botts_Dots', index=5, number=5,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Invalid', index=6, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=327,
  serialized_end=427,
)

_LANE_MODEL_DEGREE = descriptor.EnumDescriptor(
  name='Model_Degree',
  full_name='mbly.Lane.Model_Degree',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='Linear', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Parabolic', index=1, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Cubic', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=429,
  serialized_end=481,
)

_LANE_QUALITY = descriptor.EnumDescriptor(
  name='Quality',
  full_name='mbly.Lane.Quality',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='Low_Quality_0', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Low_Quality_1', index=1, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='High_Quality_2', index=2, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='High_Quality_3', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=483,
  serialized_end=570,
)

_LANE_VIEW_RANGE_AVAILIBILITY = descriptor.EnumDescriptor(
  name='View_Range_Availibility',
  full_name='mbly.Lane.View_Range_Availibility',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='Not_Valid', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='Valid', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=572,
  serialized_end=623,
)


_LANE = descriptor.Descriptor(
  name='Lane',
  full_name='mbly.Lane',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='timestamp', full_name='mbly.Lane.timestamp', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='lane_id', full_name='mbly.Lane.lane_id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='C0', full_name='mbly.Lane.C0', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='C1', full_name='mbly.Lane.C1', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='C2', full_name='mbly.Lane.C2', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='C3', full_name='mbly.Lane.C3', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='lane_type', full_name='mbly.Lane.lane_type', index=6,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='model_degree', full_name='mbly.Lane.model_degree', index=7,
      number=8, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='quality', full_name='mbly.Lane.quality', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='view_range_availability', full_name='mbly.Lane.view_range_availability', index=9,
      number=10, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='view_range', full_name='mbly.Lane.view_range', index=10,
      number=11, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _LANE_TYPE,
    _LANE_MODEL_DEGREE,
    _LANE_QUALITY,
    _LANE_VIEW_RANGE_AVAILIBILITY,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=26,
  serialized_end=623,
)


_LANES = descriptor.Descriptor(
  name='Lanes',
  full_name='mbly.Lanes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='lane', full_name='mbly.Lanes.lane', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=625,
  serialized_end=658,
)


_LANE.fields_by_name['lane_type'].enum_type = _LANE_TYPE
_LANE.fields_by_name['model_degree'].enum_type = _LANE_MODEL_DEGREE
_LANE.fields_by_name['quality'].enum_type = _LANE_QUALITY
_LANE.fields_by_name['view_range_availability'].enum_type = _LANE_VIEW_RANGE_AVAILIBILITY
_LANE_TYPE.containing_type = _LANE;
_LANE_MODEL_DEGREE.containing_type = _LANE;
_LANE_QUALITY.containing_type = _LANE;
_LANE_VIEW_RANGE_AVAILIBILITY.containing_type = _LANE;
_LANES.fields_by_name['lane'].message_type = _LANE

class Lane(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LANE
  
  # @@protoc_insertion_point(class_scope:mbly.Lane)

class Lanes(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LANES
  
  # @@protoc_insertion_point(class_scope:mbly.Lanes)

# @@protoc_insertion_point(module_scope)