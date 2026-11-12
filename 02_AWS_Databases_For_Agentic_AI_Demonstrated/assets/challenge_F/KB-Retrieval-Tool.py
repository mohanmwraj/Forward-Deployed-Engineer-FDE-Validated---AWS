"""KB Retrieve Tool Lambda - Retrieves documents from Bedrock Knowledge Base."""
import json
import os
import boto3

REGION = os.environ.get("AWS_REGION_OVERRIDE", "us-east-1")
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "")

bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=REGION)


def handler(event, context):
    """Retrieve relevant documents from the Knowledge Base.
    
    Input:
        query: Natural language search query
        max_results: Number of results to return (default 3)
    
    Returns:
        Relevant document chunks with source metadata
    """
    query = event.get("query", "")
    max_results = event.get("max_results", 3)

    if not query:
        return {"statusCode": 400, "error": "Missing 'query' parameter"}

    if not KNOWLEDGE_BASE_ID:
        return {
            "statusCode": 503,
            "error": "KNOWLEDGE_BASE_ID not configured. Create the Knowledge Base in Challenge 4 and set the ID."
        }

    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": max_results}
            }
        )

        results = []
        for result in response.get("retrievalResults", []):
            content = result.get("content", {}).get("text", "")
            metadata = result.get("metadata", {})
            score = result.get("score", 0)
            location = result.get("location", {})
            
            results.append({
                "content": content,
                "score": score,
                "source": location.get("s3Location", {}).get("uri", "unknown"),
                "metadata": metadata,
            })

        return {
            "statusCode": 200,
            "results": results,
            "count": len(results),
        }

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}
