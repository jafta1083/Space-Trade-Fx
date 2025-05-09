def status_code(code):
    """
    Returns a short message explaining what an HTTP status code means.

    :param code: Integer HTTP status code (e.g. 200, 404)
    :return: String message
    """
    status_messages = {
        200: "OK - Everything went well.",
        201: "Created - The request was successful and a new resource was created.",
        204: "No Content - The request was successful but there's no response body.",
        400: "Bad Request - The server could not understand the request.",
        401: "Unauthorized - You need to provide valid credentials.",
        403: "Forbidden - You're not allowed to access this resource.",
        404: "Not Found - The resource does not exist.",
        408: "Request Timeout - The server timed out waiting for the request.",
        429: "Too Many Requests - You are being rate limited.",
        500: "Internal Server Error - The server failed to fulfill the request.",
        502: "Bad Gateway - Invalid response from upstream server.",
        503: "Service Unavailable - The server is temporarily down or busy.",
        504: "Gateway Timeout - The upstream server failed to respond in time."
    }

    return status_messages.get(code, f"Unknown Status Code: {code}")

