import threading
import time


class MetricsManager:

    def __init__(self):
        self._lock = threading.Lock()

        self.request_count = 0
        self.success_count = 0
        self.error_count = 0

        self.total_latency = 0.0
        self.max_latency = 0.0

        self.started_at = time.time()

    def record_request(
        self,
        latency,
        success=True,
    ):
        with self._lock:

            self.request_count += 1

            self.total_latency += latency

            if latency > self.max_latency:
                self.max_latency = latency

            if success:
                self.success_count += 1
            else:
                self.error_count += 1

    def get_metrics(self):

        with self._lock:

            average_latency = 0.0

            if self.request_count:
                average_latency = (
                    self.total_latency
                    / self.request_count
                )

            error_rate = 0.0

            if self.request_count:
                error_rate = (
                    self.error_count
                    / self.request_count
                ) * 100

            uptime = (
                time.time()
                - self.started_at
            )

            return {
                "request_count":
                    self.request_count,

                "success_count":
                    self.success_count,

                "error_count":
                    self.error_count,

                "error_rate":
                    round(error_rate, 2),

                "average_latency_ms":
                    round(
                        average_latency * 1000,
                        2,
                    ),

                "max_latency_ms":
                    round(
                        self.max_latency * 1000,
                        2,
                    ),

                "uptime_seconds":
                    round(uptime, 2),
            }


metrics = MetricsManager()