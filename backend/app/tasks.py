from celery import shared_task
from app.services import storage, aws_nova, reporting, email,forensic_service

# --- THIS DECORATOR MAKES IT A CELERY TASK ---
@shared_task(name="process_audio_pipeline", bind=True, max_retries=3)
def process_audio_pipeline(self, s3_key: str, user_email: str):
    """
    This function runs on the Worker (Redis), NOT the Web Server.
    """
    try:
        print(f"Starting analysis for: {s3_key}")

        # 1. Get secure link
        file_url = storage.get_presigned_url(s3_key)

        #signal procesing forensics (forgery detection)
        processing_result = forensic_service.ForensicService._analyze_signal_integrity(
            file_path=file_url
        )
        
        # 2. Call AWS Nova (Heavy AI work)
        ai_result = aws_nova.analyze_transcript(file_url)


        # 3. Create Report
        final_report = reporting.compile_forensic_report(
            ai_result, 
            {"filename": s3_key}
        )
        
        # 4. Email User
        # Note: We use a synchronous wrapper or fire-and-forget here
        # since Celery tasks are already async.
        print(f"Analysis done. Emailing {user_email}...")
        
        return final_report

    except Exception as e:
        print(f"Task Failed: {e}")
        # Retry in 60 seconds if it fails
        self.retry(countdown=60)