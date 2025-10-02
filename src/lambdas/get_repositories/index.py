import json

# In a real-world scenario, this would fetch the list of available
# repositories from a database, S3, or another source.
# For now, we'll return a hardcoded list.
AVAILABLE_REPOSITORIES = [
    "modelearth/webroot",
    "modelearth/cloud", 
    "modelearth/codechat",
    "modelearth/community-forecasting",
    "modelearth/comparison",
    "modelearth/exiobase",
    "modelearth/feed",
    "modelearth/home",
    "modelearth/io",
    "modelearth/localsite",
    "modelearth/products",
    "modelearth/profile",
    "modelearth/projects",
    "modelearth/realitystream",
    "modelearth/reports",
    "modelearth/swiper",
    "modelearth/team"
]

def lambda_handler(event, context):
    """
    Handles the request to get the list of available repositories.
    """
    # Handle CORS preflight request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': ''
        }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Allow all origins
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        "body": json.dumps(AVAILABLE_REPOSITORIES)
    }
