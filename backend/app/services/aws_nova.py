import json
import logging
from botocore.exceptions import ClientError
from app.core.aws_connection import aws_client
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

def analyze_transcript(
    transcript_text: str, 
    system_instruction: str = None,
    temperature: float = 0.1
) -> dict:
    """
    Sends a transcript to Amazon Nova (Bedrock) for forensic analysis.
    
    Args:
        transcript_text: The speech-to-text content to analyze.
        system_instruction: Optional override for the AI persona/rules.
        temperature: Creativity level (0.0 = factual, 1.0 = creative).
        
    Returns:
        dict: Contains 'analysis', 'usage_metrics', and 'status'.
    """
    
    # 1. Get the Bedrock Runtime Client
    # We use the centralized client from core/aws.py
    bedrock = aws_client.get_bedrock_client()

    # 2. Define the Default Persona (if not provided)
    if not system_instruction:
        system_instruction = (
            "You are VeriJust, an expert forensic speech analyst. "
            "Your task is to analyze the following transcript for credibility. "
            "Identify potential 'bluffing', hesitation markers, logical inconsistencies, "
            "and manipulative phrasing. Provide a risk score (0-100) and a summary."
        )

    # 3. Construct the Payload (Amazon Nova Schema)
    # Nova uses the 'messages' API format.
    payload = {
        "system": [{"text": system_instruction}],
        "messages": [
            {
                "role": "user",
                "content": [{"text": transcript_text}]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 2000,
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 20
        }
    }

    try:
        # 4. Invoke the Model
        logger.info("Sending request to Amazon Nova...")
        
        response = bedrock.invoke_model(
            modelId=settings.BEDROCK_MODEL_ID,  # e.g., "amazon.nova-pro-v1:0"
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )

        # 5. Parse the Response
        response_body = json.loads(response.get("body").read())
        
        # Navigate the Nova response structure to get the text
        # Structure: output -> message -> content -> [ {text: ...} ]
        output_message = response_body.get("output", {}).get("message", {})
        content_list = output_message.get("content", [])
        
        # Combine all text blocks
        full_analysis_text = "".join(
            [item["text"] for item in content_list if "text" in item]
        )
        
        # Extract token usage for cost tracking
        usage_metrics = response_body.get("usage", {})

        return {
            "status": "success",
            "analysis": full_analysis_text,
            "input_tokens": usage_metrics.get("inputTokens", 0),
            "output_tokens": usage_metrics.get("outputTokens", 0)
        }

    except ClientError as e:
        logger.error(f"AWS Bedrock ClientError: {e}")
        return {
            "status": "error", 
            "message": f"AWS API Error: {str(e)}"
        }
        
    except Exception as e:
        logger.error(f"Unexpected Error in Nova Service: {e}")
        return {
            "status": "error", 
            "message": "Internal processing error"
        }