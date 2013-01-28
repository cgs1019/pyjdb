import spec_structures

def jdwprpc(spec):
  return "\n".join([
      "import %s" % ",".join([
          "google.protobuf.message",
          "jdwp",
          "jdwp_pb2",
          "protobuf.socketrpc.server",
          "struct",
          "sys",
          ]),
      server_creator_function(spec.command_sets),
      server_constants(spec.command_sets),
      # Error should be the first constant set...
      error_messages(spec.constant_sets[0]),
      "\n".join([ command_set_impl(cs) for cs in spec.command_sets ]),
      main_clause() ])

def main_clause():
  return "\n".join([
      "if __name__ == '__main__':",
      "  LaunchServer(int(sys.argv[1]), int(sys.argv[2]))" ])

def server_creator_function(command_sets):
  return "\n".join([
      "def LaunchServer(port, jvm_debug_port):",
      "  print(\"Launching server\")",
      "  # jdwp.Jdwp encapsulates direct wire communication with the jvm",
      "  jdwp = jdwp.Jdwp(int(jvm_debug_port))",
      "  server = protobuf.socketrpc.server.SocketRpcServer(port)",
      "\n".join([
          "  server.registerService(%sImpl(jdwp))" % cs.name for cs in command_sets
          ]),
      "  server.run()",
      "  return server",
      ])

def server_constants(command_sets):
  return "\n".join([
      "COMMAND_SPECS = dict()",
      "def command_specs_key(cmd_set_id, cmd_id):",
      "  return \"%s-%s\" % (cmd_set_id, cmd_id)",
      "\n".join(["\n".join([
          "COMMAND_SPECS[\"%s-%s\"] = (%s,%s,\"%s\",\"%s\")" % (
              command_set.id, command.id,
              command_set.id, command.id,
              command.request.pack_fmt(),
              command.response.pack_fmt()
              )
          for command in command_set.commands ])
      for command_set in command_sets ]),
      ])

def command_set_impl(cs):
  return "\n".join([
      "class %sImpl(jdwp_pb2.%s):" % (cs.name, cs.name),
      "  def __init__(self, jdwp):",
      "    self.jdwp = jdwp",
      "\n".join([ "%s" % command_impl(cs, cmd) for cmd in cs.commands ])
      ])

def command_impl(cs, cmd):
  return "\n".join([
      "  def %s_%s(self, controller, request, done):" % (cs.name, cmd.name),
      request_packing_impl(cs, cmd, cmd.request),
      jdwp_call_impl(cs, cmd),
      {
          spec_structures.Response:response_unpacking_impl,
          spec_structures.Event:event_unpacking_impl
          }[type(cmd.response)](cs, cmd, cmd.response),
      "    done.run(response)",
      ])

def request_packing_impl(cs, cmd, request):
  return "\n".join([
      "    data = []",
      "\n".join([
          request_arg_packing_impl("data", cs, cmd, arg, idx)
              for (idx, arg) in enumerate(request.args) ]),
      ])

def jdwp_call_impl(cs, cmd):
  return "\n".join([
      "    reply = self.jdwp.send_command_await_reply(%s, %s, data)" % (
          cs.id, cmd.id),
      ])

def response_unpacking_impl(cs, cmd, response):
  return "\n".join([
      "    response = jdwp_pb2.%s_%s_Response()" % (cs.name, cmd.name),
      "\n".join([
          response_arg_unpacking_impl("reply[%s]" % idx, cs, cmd, arg, idx)
          for (idx, arg) in enumerate(response.args) ]),
      ])

def event_unpacking_impl(cs, cmd, response):
  return "\n".join([
      #"    response = jdwp_pb2.%s_%s_Response()" % (cs.name, cmd.name),
      #"\n".join([
      #    response_arg_unpacking_impl("reply[%s]" % idx, cs, cmd, arg, idx)
      #    for (idx, arg) in enumerate(response.args) ]),
      ])

def request_arg_packing_impl(data, cs, cmd, arg, idx):
  return {
      spec_structures.Simple:simple_request_arg_unpacking_impl,
      spec_structures.Repeat:repeat_request_arg_unpacking_impl,
      }[type(arg)](data, cs, cmd, arg, idx)

def simple_request_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return "    data.append(request.%s)" % arg.name

def repeat_request_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return {
      spec_structures.Simple:simple_repeat_request_arg_unpacking_impl,
      spec_structures.Group:group_repeat_request_arg_unpacking_impl,
      spec_structures.Select:select_repeat_request_arg_unpacking_impl
      }[type(arg.arg)](data, cs, cmd, arg, idx)

def simple_repeat_request_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return "\n".join([
      "    data.append(request.%s)" % arg.name,
      "    # stuff we have here:",
      "    # %s" % [arg.arg.type, arg.arg.name]
      ])

def group_repeat_request_arg_unpacking_impl(data, cs, cmd, arg, idx):
  group = arg.arg
  return "\n".join([
      "    for item in request.%s:" % arg.name,
      "      new_item = request.%s.add()" % arg.name,
      "\n".join([
          "      new_item.%s = item[%s]" % (sub_arg.name, idx)
              for (idx, sub_arg) in enumerate(group.args) ])
      ])

def select_repeat_request_arg_unpacking_impl(data, cs, cmd, arg, idx):
  select = arg.arg
  return "\n".join([
      "    select_repeat = []",
      "    for item in request.%s:" % arg.name,
      "      select_repeat.append(jdwp.proto_to_data(item))",
      "    data.append(select_repeat)",
      ])

def response_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return {
      spec_structures.Simple:simple_response_arg_unpacking_impl,
      spec_structures.Repeat:repeat_response_arg_unpacking_impl,
      }[type(arg)](data, cs, cmd, arg, idx)

def simple_response_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return "    response.%s = %s" % (arg.name, data)

def repeat_response_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return { spec_structures.Simple:simple_repeat_response_arg_unpacking_impl,
      spec_structures.Group:group_repeat_response_arg_unpacking_impl,
      spec_structures.Select:select_repeat_response_arg_unpacking_impl
      }[type(arg.arg)](data, cs, cmd, arg, idx)

def simple_repeat_response_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return "\n".join([
      "    response.%s.extend([ i[0] for i in %s ])" % (arg.name, data),
      ])

def group_repeat_response_arg_unpacking_impl(data, cs, cmd, arg, idx):
  group = arg.arg
  return "\n".join([
      "    for item in %s:" % data,
      "      new_item = response.%s.add()" % arg.name,
      "\n".join([
          "      new_item.%s = item[%s]" % (sub_arg.name, idx)
              for (idx, sub_arg) in enumerate(group.args) ])
      ])

def select_repeat_response_arg_unpacking_impl(data, cs, cmd, arg, idx):
  return "    response.%s = %s" % (arg.name, data)

def error_messages(spec_error_constant_set):
  return "\n".join([
    "ERROR_MESSAGES = dict([",
    "\n".join([
      "    (%s, \"%s\")," % (constant.value, constant.name[len("Error_"):]) \
          for constant in spec_error_constant_set.constants
        ]),
    "])",
    "def print_error(err, request_id, cmd_set_id, cmd_id, request):",
    "  print(\"JdwpError %d: req_id:%d, cmd:(%d,%d), req:%s, %s: '%s'\" % (",
    "      err,",
    "      request_id,",
    "      cmd_set_id,",
    "      cmd_id,",
    "      request,",
    "      ERROR_MESSAGES[err][0],",
    "      ERROR_MESSAGES[err][1]))",
    ])
