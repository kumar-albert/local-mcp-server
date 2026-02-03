import boto3
from src.utils import extract_json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def think_with_bedrock(conversation: str) -> dict:
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=conversation,
        inferenceConfig={"maxTokens": 128, "temperature": 0.8, "topP": 0.9},
    ) 
    response_text = response["output"]["message"]["content"][0]["text"]
    return extract_json(response_text)
