from datetime import datetime


# -------------------- UTILITIES --------------------

def parse_lgs(lgs_raw: str) -> str:
    """Convert 'vm012.net(9);vm013.net(9);' → 'vm012.net (9), vm013.net (9)'"""
    if not lgs_raw:
        return ""
    entries = [e for e in lgs_raw.split(";") if e.strip()]
    return ", ".join(e.strip() for e in entries)

def safe_parse_time(timestring: str):
    if not timestring:
        return None
    try:
        return datetime.fromisoformat(timestring)
    except ValueError:
        return None

def compute_duration(start: str, end: str) -> str:
    t1 = safe_parse_time(start)
    t2 = safe_parse_time(end)
    if not t1 or not t2:
        return "00:00:00"
    diff = (t2 - t1).total_seconds()
    hrs = int(diff // 3600)
    mins = int((diff % 3600) // 60)
    secs = int(diff % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def chunk_list(items, chunk_size):
    """Split a list into chunks of given size."""
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

class RunSummary:
    def __init__(self, run: dict, settings=None):
        self.run = run
        self.settings = settings

    def _get(self, key: str, default=""):
        value = self.run.get(key, default)
        return "" if value is None else str(value)

    def build_rows(self):
        """Build main table rows WITHOUT LGs, includes start/end times."""
        rows = [
            [
                f"Domain: {getattr(self.settings, 'lre_domain', '')}",
                f"Project: {getattr(self.settings, 'lre_project', '')}",
                f"Test Name: {self._get('TestName')}",
                f"Test Id: {self._get('TestId')}",
            ],
            [
                f"Run Name: {self._get('Name')}",
                f"Start Time: {self._get('Start')}",
                f"End Time: {self._get('End')}",
                f"Duration: {compute_duration(self._get('Start'), self._get('End'))}",
            ],
            [
                f"Run ID: {getattr(self.settings, 'lre_run_id', '')}",
                f"Run Status: {self._get('State')}",
                f"Controller: {self._get('Controller')}",
                f"Test Instance Id: {self._get('TestInstanceId')}",

            ],
            [
                f"Vusers Involved: {self._get('VusersInvolved')}",
                f"Trans Passed: {self._get('TransPassed')}",
                f"Trans Failed: {self._get('TransFailed')}",
                f"Errors: {self._get('Errors')}",
            ],
            [
                f"Trans/sec: {self._get('TransPerSec')}",
                f"Hits/sec: {self._get('HitsPerSec')}",
                f"Throughput Avg: {self._get('ThroughputAvg')}",
                ""
            ]
        ]
        return rows

    def get_lgs_list(self):
        """Return a list of LGs, empty list if none."""
        lgs_raw = self._get("LGs")
        if not lgs_raw:
            return []
        return [e.strip() for e in lgs_raw.split(";") if e.strip()]

# -------------------- TABLE PRINTER --------------------

class TablePrinter:
    @staticmethod
    def _visible_len(s: str) -> int:
        return len(s)

    @classmethod
    def print(cls, rows):
        num_cols = len(rows[0])
        col_widths = [0] * num_cols

        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], cls._visible_len(cell))

        border = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        print(border)
        for row in rows:
            padded_cells = []
            for i, cell in enumerate(row):
                padding = col_widths[i] - cls._visible_len(cell)
                padded_cells.append(" " + cell + " " * (padding + 1))
            print("|" + "|".join(padded_cells) + "|")
        print(border)


