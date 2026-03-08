"""Length-prefixed socket transport helpers for Better Together."""

from .config import NETWORK_BUFFER_SIZE
from .protocol import deserialize_message, serialize_message


MESSAGE_LENGTH_HEADER_SIZE = 4
MAX_MESSAGE_SIZE = NETWORK_BUFFER_SIZE


class TransportError(Exception):
    """Base exception for framed transport failures."""


class ConnectionClosedError(TransportError):
    """Raised when the peer closes the connection before a message arrives."""


class IncompleteMessageError(TransportError):
    """Raised when the peer closes the connection mid-message."""


class InvalidMessageHeaderError(TransportError):
    """Raised when the message length header is invalid."""


class MessageTooLargeError(TransportError):
    """Raised when a framed message exceeds the supported size limit."""


class MessageDecodeError(TransportError):
    """Raised when a framed payload cannot be decoded into a protocol message."""


def frame_message(message):
    payload = serialize_message(message)
    payload_length = len(payload)
    if payload_length <= 0:
        raise InvalidMessageHeaderError("Transport payloads must be non-empty.")
    if payload_length > MAX_MESSAGE_SIZE:
        raise MessageTooLargeError(
            f"Transport payload length {payload_length} exceeds max size {MAX_MESSAGE_SIZE}."
        )

    return payload_length.to_bytes(MESSAGE_LENGTH_HEADER_SIZE, "big") + payload


def send_message(connection, message):
    connection.sendall(frame_message(message))


def recv_exactly(connection, byte_count):
    if byte_count <= 0:
        return b""

    payload = bytearray()
    while len(payload) < byte_count:
        chunk_size = min(byte_count - len(payload), NETWORK_BUFFER_SIZE)
        chunk = connection.recv(chunk_size)
        if not chunk:
            if not payload:
                raise ConnectionClosedError(
                    f"Connection closed while waiting for {byte_count} bytes."
                )

            raise IncompleteMessageError(
                f"Connection closed after {len(payload)} of {byte_count} bytes."
            )

        payload.extend(chunk)

    return bytes(payload)


def receive_message(connection):
    header = recv_exactly(connection, MESSAGE_LENGTH_HEADER_SIZE)
    payload_length = int.from_bytes(header, "big")
    if payload_length <= 0:
        raise InvalidMessageHeaderError(
            f"Invalid message length {payload_length}; expected a positive payload length."
        )
    if payload_length > MAX_MESSAGE_SIZE:
        raise MessageTooLargeError(
            f"Transport payload length {payload_length} exceeds max size {MAX_MESSAGE_SIZE}."
        )

    payload = recv_exactly(connection, payload_length)
    try:
        return deserialize_message(payload)
    except Exception as err:  # pragma: no cover - exact pickle failures vary by payload/runtime.
        raise MessageDecodeError("Could not decode transport payload.") from err


__all__ = [
    "ConnectionClosedError",
    "IncompleteMessageError",
    "InvalidMessageHeaderError",
    "MAX_MESSAGE_SIZE",
    "MESSAGE_LENGTH_HEADER_SIZE",
    "MessageDecodeError",
    "MessageTooLargeError",
    "TransportError",
    "frame_message",
    "receive_message",
    "recv_exactly",
    "send_message",
]
