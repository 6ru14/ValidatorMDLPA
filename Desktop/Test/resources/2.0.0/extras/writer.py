import os
import csv
import pandas as pd
import tempfile

# Set up temporary directory and raport file path
REPORT_DIR = tempfile.gettempdir()
REPORT_PATH = os.path.join(REPORT_DIR, 'report.csv')

class ReportWriter:
    """Handles the creation and writing of report data to a CSV file."""
    
    @staticmethod
    def clear_csv(path: str = REPORT_PATH) -> None:
        """Clears all content from the CSV file."""
        with open(path, 'w') as file:
            file.truncate()

    @staticmethod
    def write_headers(path: str = REPORT_PATH) -> None:
        """Writes the CSV headers."""
        headers = ["Nr. Regula", "Status", "Tip Alerta", "Regula", "Mesaj", "Modificare", "Verifica"]
        with open(path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

    @staticmethod
    def _format_alert_type(alert_type: str) -> str:
        """Converts numeric alert type to human-readable string."""
        alert_type = str(alert_type).strip()
        if alert_type.isdigit():
            alert_mapping = {1: "Blocker", 2: "Warning"}
            return alert_mapping.get(int(alert_type), alert_type)
        return alert_type

    @staticmethod
    def write_pass(rule: pd.DataFrame, path: str = REPORT_PATH) -> None:
        """Writes a passing rule entry to the CSV."""
        row = [
            rule['numar_regula'],
            "Pass",
            ReportWriter._format_alert_type(rule["tip_alerta_id"]),
            rule["descriere"],
            rule["pass_alerta"],
            "-",
            "-"
        ]
        with open(path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    @staticmethod
    def write_fail(rule: pd.DataFrame, verify: str = "-", path: str = REPORT_PATH) -> None:
        """Writes a failing rule entry to the CSV."""
        row = [
            rule['numar_regula'],
            "Fail",
            ReportWriter._format_alert_type(rule["tip_alerta_id"]),
            rule["descriere"],
            rule["fail_alerta"],
            rule['mesaj_modificare'],
            verify
        ]
        with open(path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    @staticmethod
    def write_error(rule: pd.DataFrame, verify: str = "-", path: str = REPORT_PATH) -> None:
        """Writes an error rule entry to the CSV."""
        row = [
            rule['numar_regula'],
            "Error",
            ReportWriter._format_alert_type(rule["tip_alerta_id"]),
            rule["descriere"],
            rule["error_alerta"],
            rule['eroare_modificare'],
            verify
        ]
        with open(path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)