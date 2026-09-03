# CareLedger outpatient records

A local Python desktop application for maintaining outpatient records, including:

- Demographic data and emergency contact details
- Case history, examination and investigations
- Diagnosis, treatment and follow-up advice
- Searchable patient registry with persistent SQLite storage

## Run

```powershell
python main.py
```

The application creates `outpatient_records.db` in the same folder on first run. It is intended for local development and demonstration; add authentication, encryption, backups and an approved clinical data policy before using it with real patient data.