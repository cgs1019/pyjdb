import os
import pyjdb
import signal
import string
import subprocess
import time
import unittest

class TestJdwpPackage(unittest.TestCase):
    def setUp(self):
        # boot up the sample java program in target jvm
        self.test_target_subprocess = subprocess.Popen([
            "/usr/bin/java", "-cp", "java_sample/fib.jar",
            "-Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=5005",
            "com.alltheburritos.vimjdb.test.TestProgram"])
<<<<<<< HEAD
        self.jdwp = pyjdb.Jdwp("localhost", 5005)
=======
        self.jdwp = pyjdb.Jdwp('localhost', 5005)
>>>>>>> bac72cf2b133e9be23858edc2154ba3501ec9037
        self.jdwp.initialize();

    def tearDown(self):
        # disconnect debugger
        self.jdwp.disconnect()
        # kill target jvm
        self.test_target_subprocess.send_signal(signal.SIGKILL)
        self.test_target_subprocess.wait()
<<<<<<< HEAD
=======

    def handle_event(self, req_id, event):
        self.events.append(event)
>>>>>>> bac72cf2b133e9be23858edc2154ba3501ec9037

    def test_virtual_machine_version(self):
        system_java_version = subprocess.check_output(
            "java -version 2>&1", shell=True)
        # the java -version output looks like
        #   java version "1.7.0_09"
        #   OpenJDK Runtime Environment .....
        #   OpenJDK 64-Bit Server VM (build 23.2-b09, mixed mode)
        # below, the inner split splits on any whitespace - the version is the 3rd
        # token (the 2th, from 0). It"s double-quoted so we split on double-quotes
        # and take the middle one.
        system_version_number = string.split(
            string.split(system_java_version)[2], "\"")[1]
        version_response = self.jdwp.VirtualMachine.Version()
        jdwp_jvm_version_number = version_response["vmVersion"]
        # if they"re equal, then we"re in business!
        self.assertEquals(system_version_number, jdwp_jvm_version_number)

<<<<<<< HEAD
    def test_virtual_machine_all_classes(self):
        all_classes_response = self.jdwp.VirtualMachine.AllClasses()
        self.assertTrue(all_classes_response["classes"] != None)
        string_class = [ x for x in all_classes_response["classes"] if
            x["signature"] == u"Ljava/lang/String;" ]
        self.assertEquals(len(string_class), 1)

    def test_event_request_set_and_resume(self):
        # in this test we will
        #   1. get a list of all loaded classes
        #   2. request notification of class load events
        #   3. resume our suspended program
        #   4. assert that com.alltheburritos.defbug.test.TestProgram gets loaded
        all_classes_response = self.jdwp.VirtualMachine.AllClasses()
        loaded_class_signatures =\
            [ entry["signature"] for entry in all_classes_response["classes"] ]
        self.jdwp.EventRequest.Set({
            "eventKind": self.jdwp.EventKind.CLASS_PREPARE,
            "suspendPolicy": self.jdwp.SuspendPolicy.NONE,
            "modifiers": []})
        # send vm resume to start things off
        self.jdwp.VirtualMachine.Resume()
        test_sig = u"Lcom/alltheburritos/vimjdb/test/TestProgram;"
        def matches(whole_event):
            _, events = whole_event
            for event in events["events"]:
                if "ClassPrepare" in event:
                    class_prepare_event = event["ClassPrepare"]
                    if class_prepare_event["signature"] == test_sig:
                        return True
            return False
        class_prepare_event = self.jdwp.await_event(matches)
        self.assertIsNotNone(class_prepare_event)

    def test_set_breakpoint(self):
        # we have to first await the loading of our class, so we set an event.
        test_class = "com.alltheburritos.vimjdb.test.TestProgram"
        test_sig = u"Lcom/alltheburritos/vimjdb/test/TestProgram;"
        self.jdwp.EventRequest.Set({
                "eventKind": self.jdwp.EventKind.CLASS_PREPARE,
                "suspendPolicy": self.jdwp.SuspendPolicy.ALL,
                "modifiers": [{
                        "modKind": 5,
                        "Modifier": {"classPattern": test_class}}]})
        # send vm resume to start things off
        self.jdwp.VirtualMachine.Resume()
        # wait for class prepare event
        def matches(whole_event):
            _, event = whole_event
            for event in event["events"]:
                if event["eventKind"] == self.jdwp.EventKind.CLASS_PREPARE:
                    return event["ClassPrepare"]["signature"] == test_sig
        event = self.jdwp.await_event(matches)
        class_prepare_event = event[1]["events"][0]
        class_id = class_prepare_event["ClassPrepare"]["typeID"]
        # get class methods
        resp = self.jdwp.ReferenceType.Methods({"refType": class_id})
        for method in resp["declared"]:
            if method["name"] == u"main":
                # find main method id
                main_method_id = method["methodID"]
        # set breakpoint
        resp = self.jdwp.EventRequest.Set({
                "eventKind": self.jdwp.EventKind.BREAKPOINT,
                "suspendPolicy": self.jdwp.SuspendPolicy.ALL,
                "modifiers": [{
                        "modKind": 7,
                        "Modifier": {
                                "loc": {
                                        "typeTag": self.jdwp.TypeTag.CLASS,
                                        "classID": class_id,
                                        "methodID": main_method_id,
                                        "index": 0}}}]})
        breakpoint_request_id = resp["requestID"]
        # send vm resume
        self.jdwp.VirtualMachine.Resume()
        # wait for breakpoint event
        def matches(whole_event):
            _, event = whole_event
            for event in event["events"]:
                if event["eventKind"] == self.jdwp.EventKind.BREAKPOINT:
                    return True
        _, event = self.jdwp.await_event(matches)
        event = event["events"][0]
        # breakpoint should look as expected
        self.assertTrue("Breakpoint" in event)
        self.assertEquals(
                breakpoint_request_id, event["Breakpoint"]["requestID"])
        self.assertEquals(
                class_id, event["Breakpoint"]["location"]["classID"])
        self.assertEquals(
                main_method_id, event["Breakpoint"]["location"]["methodID"])
        self.assertEquals(
                self.jdwp.TypeTag.CLASS, event["Breakpoint"]["location"]["typeTag"])
        self.assertEquals(
                0, event["Breakpoint"]["location"]["index"])

if __name__ == "__main__":
=======
    #def test_virtual_machine_all_classes(self):
    #    all_classes_response = self.jdwp.VirtualMachine.AllClasses()
    #    self.assertTrue(all_classes_response['classes'] != None)
    #    string_class = [ x for x in all_classes_response['classes'] if
    #        x['signature'] == u'Ljava/lang/String;' ]
    #    self.assertEquals(len(string_class), 1)

    #def test_event_request_set_and_resume(self):
    #    # in this test we will
    #    #   1. get a list of all loaded classes
    #    #   2. request notification of class load events
    #    #   3. resume our suspended program
    #    #   4. assert that com.alltheburritos.defbug.test.TestProgram gets loaded
    #    all_classes_response = self.jdwp.VirtualMachine.AllClasses()
    #    loaded_class_signatures =\
    #        [ entry['signature'] for entry in all_classes_response['classes'] ]
    #    self.jdwp.EventRequest.Set({
    #        "eventKind": self.jdwp.EventKind.CLASS_PREPARE,
    #        "suspendPolicy": self.jdwp.SuspendPolicy.NONE,
    #        "modifiers": []})
    #    # send vm resume to start things off
    #    self.jdwp.VirtualMachine.Resume()
    #    time.sleep(.5)
    #    self.assertGreater(len(self.events), 0)
    #    test_sig = u'Lcom/alltheburritos/vimjdb/test/TestProgram;'
    #    found_test_class = False
    #    for composite in self.events:
    #        for event in composite["events"]:
    #            if event["events"]["signature"] == test_sig:
    #                found_test_class = True
    #                break
    #    self.assertTrue(found_test_class) 

    #def test_set_breakpoint(self):
    #    # we have to first await the loading of our class, so we set an event.
    #    test_class = "com.alltheburritos.vimjdb.test.TestProgram"
    #    self.jdwp.EventRequest.Set({
    #            "eventKind": jdwp_pb2.EventKind_CLASS_PREPARE,
    #            "SuspendPolicy": jdwp_pb2.SuspendPolicy_ALL,
    #            "modifiers": [{
    #                    "modKind": 5,
    #                    "classPattern": test_class}]})
    #    # send vm resume to start things off
    #    self.jdwp.VirtualMachine.Resume()
    #    # wait for class prepare event
    #    def matches(event):
    #        if event["eventKind"] == self.jdwp.EventKind.CLASS_PREPARE:
    #            return event["ClassPrepare"]["signature"] == test_class
    #    class_prepare_event = self.jdwp.await_event_kind(matcher = matches)
    #    class_id = class_prepare_event[1][1][3]
    #    # get class methods
    #    err, data = self.jdwp.send_command_await_reply(2, 5, [class_id])
    #    for method in data:
    #        if method[1] == u'main':
    #       # find main method id
    #       main_method_id = method[0]
    #   # set breakpoint
    #   breakpoint_request = [
    #       jdwp_pb2.EventKind_BREAKPOINT,
    #       jdwp_pb2.SuspendPolicy_ALL,
    #       [7, [(1, class_id, main_method_id, 0)]]]
    #   err, data = self.jdwp.send_command_await_reply(15, 1, breakpoint_request)
    #   breakpoint_request_id = data[0]
    #   # send vm resume
    #   self.jdwp.send_command_await_reply(1, 9)
    #   # wait for breakpoint event
    #   request_id, breakpoint_event = \
    #       self.await_event_kind(jdwp_pb2.EventKind_BREAKPOINT, 1)
    #   expected_breakpoint_event = \
    #       [jdwp_pb2.SuspendPolicy_ALL,
    #           [jdwp_pb2.EventKind_BREAKPOINT,
    #               [breakpoint_request_id,
    #                1,  # thread_id (get programmatically?)
    #                (1, class_id, main_method_id, 0)]]]
    #   # breakpoint should look as expected
    #   self.assertEquals(breakpoint_event, expected_breakpoint_event)

if __name__ == '__main__':
>>>>>>> bac72cf2b133e9be23858edc2154ba3501ec9037
  unittest.main()
