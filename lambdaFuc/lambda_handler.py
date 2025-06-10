def lambda_handler(event, context):
    # Always validate user input from event
    if 'user_data' in event:
        # Validate and sanitize before using
        user_input = event.get('user_data', '')
        validated_input = validate_and_sanitize(user_input)
        
        # Use the validated data for processing
        result = process_data(validated_input)
        
        return {
            'statusCode': 200,
            'body': result
        }
    else:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters'
        }
