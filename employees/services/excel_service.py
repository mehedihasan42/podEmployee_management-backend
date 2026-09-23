import os
from datetime import datetime, time

import openpyxl


MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".xlsx"}


def validate_excel_file(uploaded_file):
    if not uploaded_file:
        raise ValueError("Please upload an Excel file")

    extension = os.path.splitext(uploaded_file.name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only Excel files (.xlsx) are allowed")

    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValueError("File size cannot exceed 5 MB")


def normalize_key(value):
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def read_excel(uploaded_file):
    workbook = openpyxl.load_workbook(
        uploaded_file,
        data_only=True
    )

    worksheet = workbook.active

    rows = list(worksheet.iter_rows(values_only=True))

    if not rows:
        return []

    headers = [
        normalize_key(header)
        if header is not None
        else ""
        for header in rows[0]
    ]

    data = []

    for row in rows[1:]:
        item = {}

        for index, header in enumerate(headers):
            if not header:
                continue

            item[header] = (
                row[index]
                if index < len(row)
                else ""
            )

        # Ignore completely empty rows
        if any(
            value not in ("", None)
            for value in item.values()
        ):
            data.append(item)

    return data


def format_excel_time(value):
    if value in ("", None):
        return None

    if isinstance(value, datetime):
        return value.time().replace(
            second=0,
            microsecond=0
        )

    if isinstance(value, time):
        return value.replace(
            second=0,
            microsecond=0
        )

    # Excel time fraction
    if isinstance(value, (int, float)):
        total_minutes = round(
            float(value) * 24 * 60
        )

        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60

        return time(
            hour=hours,
            minute=minutes
        )

    text = str(value).strip()

    for fmt in (
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p",
        "%I:%M:%S %p",
    ):
        try:
            parsed = datetime.strptime(text, fmt)

            return parsed.time().replace(
                second=0,
                microsecond=0
            )
        except ValueError:
            continue

    return None


def calculate_working_hours(entry_time, exit_time):
    if not entry_time or not exit_time:
        return 0

    entry_minutes = (
        entry_time.hour * 60 +
        entry_time.minute
    )

    exit_minutes = (
        exit_time.hour * 60 +
        exit_time.minute
    )

    worked_minutes = (
        exit_minutes - entry_minutes
    )

    # Overnight shift
    if worked_minutes < 0:
        worked_minutes += 24 * 60

    return round(
        worked_minutes / 60,
        2
    )