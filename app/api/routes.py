def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-KEY')
        if not provided_key:
            return jsonify({'error': 'Missing API key. Include X-API-KEY in request headers.'}), 401

        # Search for a matching key in the database
        # We iterate through all active keys and check each one
        active_keys = APIKey.query.filter_by(is_active=True).all()
        
        valid_key_record = None
        for key_record in active_keys:
            if key_record.check_key(provided_key):
                valid_key_record = key_record
                break
        
        if valid_key_record:
            # Store the authenticated user in the request context for later use
            request.current_user = valid_key_record.owner
            return f(*args, **kwargs)
        
        return jsonify({'error': 'Invalid or inactive API key.'}), 401
    
    return decorated_function
