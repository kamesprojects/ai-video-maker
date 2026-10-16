"""Shared test doubles. Nothing here talks to the network or bills credits."""

import struct
import types


def fake_mp4(width: int, height: int, rotated: bool = False) -> bytes:
    """Minimal MP4 bytes (moov > trak > tkhd) that utils.video_size can parse."""
    matrix = [0, 0x10000, 0, -0x10000, 0, 0, 0, 0, 0x40000000] if rotated \
        else [0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000]
    tkhd_body = (
        b"\x00\x00\x00\x00"            # version 0 + flags
        + b"\x00" * 20                 # ctime, mtime, track id, reserved, duration
        + b"\x00" * 16                 # reserved, layer, alt group, volume, reserved
        + struct.pack(">9i", *matrix)
        + struct.pack(">II", width << 16, height << 16)
    )

    def box(box_type: bytes, body: bytes) -> bytes:
        return struct.pack(">I", 8 + len(body)) + box_type + body

    return box(b"ftyp", b"isom") + box(b"moov", box(b"trak", box(b"tkhd", tkhd_body)))


def fake_higgsfield(statuses: list[str], result: dict) -> types.ModuleType:
    """Fake higgsfield_client module.

    subscribe() replays `statuses` (class names) through on_queue_update and
    returns `result`. Calls are recorded in module.calls for assertions.
    """
    module = types.ModuleType("higgsfield_client")
    module.calls = {"uploads": [], "subscribe": None}

    for name in ["Queued", "InProgress", "Completed", "Failed", "NSFW", "Cancelled"]:
        setattr(module, name, type(name, (), {}))

    def upload_file(path):
        module.calls["uploads"].append(path)
        return f"https://fake.cdn/{path.name}"

    def subscribe(endpoint, arguments, on_enqueue=None, on_queue_update=None):
        module.calls["subscribe"] = {"endpoint": endpoint, "arguments": arguments}
        if on_enqueue:
            on_enqueue("fake-request-id")
        for name in statuses:
            if on_queue_update:
                on_queue_update(getattr(module, name)())
        return result

    def sync_client(timeout=None):
        module.calls["timeout"] = timeout
        return module   # the fake module doubles as the client

    module.upload_file = upload_file
    module.subscribe = subscribe
    module.SyncClient = sync_client
    return module
