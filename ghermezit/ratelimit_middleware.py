from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache

REQUEST_RATE_LIMIT = settings.REQUEST_RATE_LIMIT

class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for :
            ip = x_forwarded_for.split(',')[-1].strip()
        else :
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def rate_limit_check(self, request):
        current_ip = self.get_client_ip(request)
        total_calls = cache.get(current_ip)
        if total_calls :
            if total_calls >= REQUEST_RATE_LIMIT :
                return JsonResponse({'status':501, 'message':f'You have exhausted request rate limit! You can try after {cache.ttl(current_ip)} seconds.'})
            else :
                cache.set(current_ip, total_calls+1)
                return None
                #return JsonResponse({'status':200, 'message':f'You called this API', 'total_calls':total_calls})
        cache.set(current_ip, 1)
        return None
        #return JsonResponse({'status':200, 'ip':get_client_ip(request)})

    def __call__(self, request):
        ratelimit_response = self.rate_limit_check(request)
        if ratelimit_response :
            return ratelimit_response

        response = self.get_response(request)
        return response
