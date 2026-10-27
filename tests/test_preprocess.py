import unittest

from ml.preprocess import is_routine_transactional_message


class RoutineTransactionalMessageTests(unittest.TestCase):
    def test_recognizes_routine_otp_and_shipment_messages(self):
        messages = (
            "Your Google verification code is 829144. Do not share this one-time code with anyone.",
            "Your package containing Computer Science textbooks has been shipped and is scheduled for delivery today by 5 PM.",
        )
        for message in messages:
            with self.subTest(message=message):
                self.assertTrue(is_routine_transactional_message(message))

    def test_rejects_transactional_messages_with_scam_signals(self):
        messages = (
            "Your verification code is 829144. Claim your free prize now.",
            "Your package has shipped. Click http://example.com to pay a delivery fee immediately.",
        )
        for message in messages:
            with self.subTest(message=message):
                self.assertFalse(is_routine_transactional_message(message))
