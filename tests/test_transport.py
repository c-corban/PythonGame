import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.transport import (
    IncompleteMessageError,
    MAX_MESSAGE_SIZE,
    MESSAGE_LENGTH_HEADER_SIZE,
    MessageDecodeError,
    MessageTooLargeError,
    frame_message,
    receive_message,
    send_message,
)


class FakeSocket:
    def __init__(self, recv_bytes=b"", chunk_sizes=None):
        self.recv_buffer = bytearray(recv_bytes)
        self.chunk_sizes = list(chunk_sizes or [])
        self.sent_payloads = []

    def recv(self, requested_size):
        if not self.recv_buffer:
            return b""

        if self.chunk_sizes:
            requested_size = min(requested_size, self.chunk_sizes.pop(0))

        chunk = bytes(self.recv_buffer[:requested_size])
        del self.recv_buffer[:requested_size]
        return chunk

    def sendall(self, data):
        self.sent_payloads.append(data)


class SharedTransportTests(unittest.TestCase):
    def test_send_message_prefixes_payload_length(self):
        socket = FakeSocket()
        message = {"kind": "ping", "value": 7}

        send_message(socket, message)

        self.assertEqual(len(socket.sent_payloads), 1)
        framed_payload = socket.sent_payloads[0]
        payload_length = int.from_bytes(
            framed_payload[:MESSAGE_LENGTH_HEADER_SIZE],
            "big",
        )
        self.assertEqual(payload_length, len(framed_payload) - MESSAGE_LENGTH_HEADER_SIZE)

    def test_receive_message_reads_fragmented_payloads(self):
        message = {"message_type": "fragmented", "value": 11}
        socket = FakeSocket(
            frame_message(message),
            chunk_sizes=[1, 1, 2, 3, 5, 8, 13],
        )

        self.assertEqual(receive_message(socket), message)

    def test_receive_message_reads_back_to_back_frames(self):
        first_message = {"message_type": "first", "value": 1}
        second_message = {"message_type": "second", "value": 2}
        socket = FakeSocket(frame_message(first_message) + frame_message(second_message))

        self.assertEqual(receive_message(socket), first_message)
        self.assertEqual(receive_message(socket), second_message)

    def test_receive_message_rejects_oversized_frames(self):
        socket = FakeSocket((MAX_MESSAGE_SIZE + 1).to_bytes(MESSAGE_LENGTH_HEADER_SIZE, "big"))

        with self.assertRaises(MessageTooLargeError):
            receive_message(socket)

    def test_receive_message_rejects_invalid_pickle_payloads(self):
        invalid_payload = b"this-is-not-a-valid-pickle-payload"
        socket = FakeSocket(
            len(invalid_payload).to_bytes(MESSAGE_LENGTH_HEADER_SIZE, "big") + invalid_payload
        )

        with self.assertRaises(MessageDecodeError):
            receive_message(socket)

    def test_receive_message_rejects_incomplete_payloads(self):
        socket = FakeSocket((10).to_bytes(MESSAGE_LENGTH_HEADER_SIZE, "big") + b"abc")

        with self.assertRaises(IncompleteMessageError):
            receive_message(socket)
