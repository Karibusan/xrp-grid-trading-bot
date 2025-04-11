import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "type": getattr(record, "type", None),
            "module": getattr(record, "module", None),
        }
        return json.dumps(log_record)