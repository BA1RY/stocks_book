import redis
from django.http import JsonResponse
from django.conf import settings
from backend.settings import BASE_DIR, REDIS_HOST, REDIS_PORT
from .redis_store import RedisStore
import json

def index(request, input):
    rs = RedisStore(connection_pool=settings.REDIS_CONN_POOL)
    input = input.upper()
    stocks = rs.get_stock_data(input)
    
    return JsonResponse(stocks, safe=False)