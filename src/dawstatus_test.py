import unittest
from src.appservice import AppServiceInbox
from src.dawstatus import DawStatus, DawStatusOp, DawStatusGet, DawStatusSetKeyValue, DawStatusTestAndSetKeyValue

class dawstatusTest(unittest.TestCase):
    def setUp(self):
        self.outbox = AppServiceInbox()
        self.receiver = AppServiceInbox()
        self.testee = dawStatus = DawStatus(self.outbox, blocking=False)

    def test_get_after_init(self):
        # when
        self.outbox.put(DawStatusGet(self.receiver))
        self.testee.check_inbox()
        # then
        self.assertEqual(self.receiver.get_nowait(), {})

    def test_set_key_value(self):
        # given
        key = "abc"
        value = "456"
        # when
        self.outbox.put(DawStatusSetKeyValue(key, value, self.receiver))
        self.outbox.put(DawStatusSetKeyValue(key, value+"1", self.receiver))
        self.outbox.put(DawStatusSetKeyValue(key+"a", value+"b", self.receiver))
        self.outbox.put(DawStatusGet(self.receiver))
        self.testee.check_inbox()
        # then
        self.assertEqual(self.receiver.get_nowait(), {key: value}) # set
        self.assertEqual(self.receiver.get_nowait(), {key: value+"1"}) # set
        self.assertEqual(self.receiver.get_nowait(), {key: value+"1", key+"a": value+"b"}) # set
        self.assertEqual(self.receiver.get_nowait(), {key: value+"1", key+"a": value+"b"}) # get
        self.assertTrue(self.receiver.empty())
        
    def test_test_and_set_key_value(self):
        # given
        key = "abc"
        value = "456"
        self.outbox.put(DawStatusSetKeyValue(key, value, self.receiver))
        # when
        newvalue = "666"
        self.outbox.put(DawStatusTestAndSetKeyValue(key, "wrong"+value, newvalue, self.receiver))
        self.outbox.put(DawStatusTestAndSetKeyValue(key, value, newvalue, self.receiver))
        self.outbox.put(DawStatusGet(self.receiver))
        self.testee.check_inbox()
        # then
        self.assertEqual(self.receiver.get_nowait(), {key: value}) # set
        self.assertEqual(self.receiver.get_nowait(), {"status": {key: value}, "success": False}) # test and set, fail
        self.assertEqual(self.receiver.get_nowait(), {"status": {key: newvalue}, "success": True}) # test and set, success
        self.assertEqual(self.receiver.get_nowait(), {key: newvalue}) # get
        