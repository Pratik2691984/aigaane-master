def handler(request, context):
    return {
        "statusCode": 200,
        "headers": { "Content-Type": "application/json" },
        "body": "{\"message\": \"Python works!\"}"
    }