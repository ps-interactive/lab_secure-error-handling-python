@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Log the full exception internally for debugging
    logger.error(f"Internal system error occurred: {error}", exc_info=True)
    
    # Return a safe, generic response to the user
    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }
    return jsonify(response), 500