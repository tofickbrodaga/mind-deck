"""
Сервис кэширования с использованием Redis
Демонстрирует использование брокера сообщений (Redis)
"""
import json
from typing import Optional, Any
try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from infrastructure.config import settings


class CacheService:
    """Сервис для кэширования данных в Redis"""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Подключиться к Redis"""
        if settings.redis_url and redis:
            try:
                self._redis = await redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
            except Exception:
                self._redis = None
    
    async def disconnect(self) -> None:
        """Отключиться от Redis"""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Установить значение в кэш с TTL"""
        if not self._redis:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            await self._redis.setex(key, ttl, serialized)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        if not self._redis:
            return False
        
        try:
            await self._redis.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if not self._redis:
            return False
        
        try:
            return bool(await self._redis.exists(key))
        except Exception:
            return False

cache_service = CacheService()


async def get_cache() -> CacheService:
    """Dependency для получения сервиса кэширования"""
    if not cache_service._redis:
        await cache_service.connect()
    return cache_service
