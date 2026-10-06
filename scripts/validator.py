import os
import sqlite3
from datetime import datetime

DB_PATH = "healthcare_edi.db"
EDI_FILE_PATH = os.path.join("data", "sample_834.edi")


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            gender TEXT,
            dob TEXT,
            plan_type TEXT,
            coverage_code TEXT,
            effective_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT,
            issue_type TEXT,
            details TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def parse_edi_834(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().replace("\n", "").strip()

    segments = [s.strip() for s in content.split("~") if s.strip()]
    records = []
    current_member = {}

    for segment in segments:
        elements = segment.split("*")
        tag = elements[0]

        if tag == "INS":
            if current_member and "member_id" in current_member:
                records.append(current_member)
            current_member = {"relationship": elements[2], "status": elements[1]}

        elif tag == "REF" and elements[1] == "0F":
            current_member["member_id"] = elements[2]

        elif tag == "NM1" and elements[1] == "IL":
            current_member["last_name"] = elements[3]
            current_member["first_name"] = elements[4]

        elif tag == "DMG":
            current_member["dob"] = elements[2]
            current_member["gender"] = elements[3]

        elif tag == "HD":
            current_member["coverage_code"] = elements[3]
            current_member["plan_type"] = (
                elements[4] if len(elements) > 4 else "UNKNOWN"
            )

        elif tag == "DTP" and elements[1] == "348":
            current_member["effective_date"] = elements[3]

    if current_member and "member_id" in current_member:
        records.append(current_member)

    return records


def validate_and_load(conn, records):
    cursor = conn.cursor()
    loaded_count = 0

    for r in records:
        member_id = r.get("member_id")
        dob = r.get("dob")
        eff_date = r.get("effective_date")

        # Regla de Calidad 1: Validar formato de fechas ANSI (YYYYMMDD)
        if dob and len(dob) != 8:
            cursor.execute(
                "INSERT INTO audit_logs (member_id, issue_type, details) VALUES (?, ?, ?)",
                (member_id, "FORMAT_ERROR", f"Invalid DOB string length: {dob}"),
            )
            continue

        # Regla de Calidad 2: Validar fecha efectiva retroactiva > 1 año
        if eff_date:
            parsed_date = datetime.strptime(eff_date, "%Y%m%d")
            if parsed_date.year < 2026:
                cursor.execute(
                    "INSERT INTO audit_logs (member_id, issue_type, details) VALUES (?, ?, ?)",
                    (
                        member_id,
                        "RETROACTIVE_ENROLLMENT",
                        f"Effective date {eff_date} is older than current cycle",
                    ),
                )

        cursor.execute(
            """
            INSERT OR REPLACE INTO members 
            (member_id, last_name, first_name, gender, dob, plan_type, coverage_code, effective_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                member_id,
                r.get("last_name"),
                r.get("first_name"),
                r.get("gender"),
                dob,
                r.get("plan_type"),
                r.get("coverage_code"),
                eff_date,
            ),
        )
        loaded_count += 1

    conn.commit()
    print(f"[OK] Ingestion complete: {loaded_count} member records loaded.")
    print(f"[OK] Quality logs recorded in audit_logs table.")


if __name__ == "__main__":
    connection = init_database()
    parsed_records = parse_edi_834(EDI_FILE_PATH)
    validate_and_load(connection, parsed_records)
    connection.close()
