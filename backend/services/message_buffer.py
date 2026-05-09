from collections import defaultdict


class MultipartMessageBuffer:
    """
    In-memory multipart SMS buffer.
    Safe for single-process deployments. Replace with Redis for multi-worker.
    """

    def __init__(self) -> None:
        self._buffer = defaultdict(lambda: defaultdict(dict))

    def add_part(
        self,
        phone_number: str,
        concat_ref: str,
        concat_part: str,
        message: str,
    ) -> None:
        parts = self._buffer[phone_number][concat_ref]
        if concat_part not in parts:
            parts[concat_part] = message

    def is_complete(self, phone_number: str, concat_ref: str, concat_total: int) -> bool:
        return len(self._buffer[phone_number][concat_ref]) >= concat_total

    def consume(self, phone_number: str, concat_ref: str, concat_total: int) -> str:
        parts = self._buffer[phone_number][concat_ref]
        combined = "".join([parts[str(i)] for i in range(1, concat_total + 1)])
        del self._buffer[phone_number][concat_ref]
        return combined
