import time

class SnowflakeGenerator:

    def __init__(self, datacenter_id, worker_id):
        self._datacenter_id = datacenter_id
        self._worker_id = worker_id
        self._sequence = 0
        self._last_timestamp = -1

    def generate_id(self):
        timestamp = int(time.time() * 1000)

        if timestamp < self._last_timestamp:
            raise Exception('Clock moved backwards. Refusing to generate ID.')

        if timestamp == self._last_timestamp:
            self._sequence = (self._sequence + 1) & 0xfff
            if self._sequence == 0:
                timestamp = self._til_next_millis(self._last_timestamp)
        else:
            self._sequence = 0

        self._last_timestamp = timestamp

        return ((timestamp - 1420041600000) << 22) | (self._datacenter_id << 17) | (self._worker_id << 12) | self._sequence

    def _til_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp