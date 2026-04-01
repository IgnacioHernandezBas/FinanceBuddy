from pathlib import Path
from finance_buddy_backend.db.session import SessionLocal
from finance_buddy_backend.services.ingestion_service import IngestionService

def main() -> None:
  path="data/raw/agencia_trib"
  data_dir=Path(path)
  pdf_files=sorted(data_dir.rglob("*.pdf"))

  if not pdf_files:
    print(f"No PDF files found in the {path} directory.")
    return
  
  with SessionLocal() as db:
    ingestion_service=IngestionService(db)
    for pdf_file in pdf_files:
      try:
        result=ingestion_service.ingest_pdf(str(pdf_file))
        print(
                    f"Ingested: {result['title']} | "
                    f"source_id={result['source_id']} | "
                    f"chunks={result['chunk_count']} | "
                    f"status={result['ingestion_status']}"
                )
      except Exception as e:
        print(f"Error ingesting {pdf_file.name}: {e}")


if __name__ == "__main__":
    main()

