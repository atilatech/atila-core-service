from corsheaders.signals import check_request_enabled


def cors_allow_particular_urls_search(sender, request, **kwargs):
    print("cors_allow_particular_urls")
    print("request.path", request.path)
    return request.path.startswith('/api/atlas/search/')


check_request_enabled.connect(cors_allow_particular_urls_search)