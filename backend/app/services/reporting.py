from datetime import datetime

def compile_forensic_report(
    ai_result: dict, 
    file_metadata: dict, 
    bluff_score: float = None
) -> dict:
    """
    Aggregates raw AI data into a user-friendly report.
    """
    
    # 1. Determine Risk Level based on Bluff Score (0.0 to 1.0)
    risk_level = "LOW"
    if bluff_score and bluff_score > 0.7:
        risk_level = "HIGH"
    elif bluff_score and bluff_score > 0.4:
        risk_level = "MEDIUM"

    # 2. Format the final JSON structure
    return {
        "report_id": file_metadata.get("id"),
        "generated_at": datetime.utcnow().isoformat(),
        "file_name": file_metadata.get("filename"),
        "forensic_summary": {
            "risk_assessment": risk_level,
            "confidence_score": ai_result.get("confidence", 0.0),
            "bluff_probability": bluff_score or 0.0
        },
        "analysis_details": {
            "transcript_summary": ai_result.get("analysis", "No analysis available"),
            "flagged_segments": ai_result.get("flagged_segments", [])
        },
        "meta": {
            "processing_time": ai_result.get("processing_time_ms"),
            "model_version": "amazon.nova-pro-v1"
        }
    }