from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache

REQUEST_RATE_LIMIT = settings.REQUEST_RATE_LIMIT
RATE_LIMIT_BLOCK_TIME = settings.RATE_LIMIT_BLOCK_TIME

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

    def exceed_rate_limit(self, request):
        current_ip = self.get_client_ip(request)
        if cache.get('restricted:' + current_ip) :
            return True
        key = 'ratelimit:' + current_ip
        total_calls = cache.get(key)
        if total_calls :
            if total_calls >= REQUEST_RATE_LIMIT :
                cache.set('restricted:' + current_ip, 1, timeout=RATE_LIMIT_BLOCK_TIME)
                return True
            else :
                cache.set(key, total_calls+1, timeout=cache.ttl(key))
                return False

        cache.set(key, 1, timeout=60)
        return False

    def __call__(self, request):
        if self.exceed_rate_limit(request) :
            return JsonResponse({'message':f'Too many requests! You can try after 5 minutes.'}, status = 429)

        response = self.get_response(request)
        return response
