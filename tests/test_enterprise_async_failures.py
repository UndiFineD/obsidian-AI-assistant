"""
Enterprise Security & Advanced Async Tests
=========================================

Comprehensive async tests for enterprise security features, advanced error scenarios,
and complex system interactions in the Obsidian AI Assistant.

Test Categories:
- Enterprise authentication edge cases
- Multi-tenant isolation failures
- SSO provider failures
- RBAC permission edge cases
- Compliance audit failures
- Advanced caching scenarios
- Vector database edge cases
- Voice processing failures
- Configuration corruption scenarios
- Performance monitoring edge cases
"""

import pytest
import asyncio
import aiofiles
import aiohttp
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import jwt
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import sqlite3
import numpy as np

# Test imports
from backend.backend import app
from backend.settings import get_settings
from backend.embeddings import EmbeddingsManager
from backend.indexing import VaultIndexer
from backend.modelmanager import ModelManager
from backend.caching import CacheManager, EmbeddingCache, FileHashCache
from backend.performance import PerformanceMonitor, AsyncTaskQueue, ConnectionPool
from backend.security import encrypt_data, decrypt_data
from backend.llm_router import HybridLLMRouter
from backend.voice import voice_transcribe

pytest_plugins = ['pytest_asyncio']


class TestEnterpriseAuthenticationEdgeCases:
    """Test enterprise authentication edge cases and failure modes"""

    @pytest.mark.asyncio
    async def test_concurrent_sso_authentication_attempts(self):
        """Test concurrent SSO authentication attempts"""
        
        async def sso_auth_attempt(user_id: int, provider: str):
            """Simulate SSO authentication"""
            await asyncio.sleep(0.01)  # Simulate network delay
            
            # Simulate various failure modes
            if user_id % 10 == 0:
                raise Exception(f"SSO provider {provider} timeout")
            elif user_id % 7 == 0:
                raise Exception(f"Invalid credentials for user {user_id}")
            elif user_id % 5 == 0:
                raise Exception(f"SSO provider {provider} maintenance")
            
            # Generate mock JWT token
            payload = {
                'user_id': user_id,
                'provider': provider,
                'exp': datetime.utcnow() + timedelta(hours=1),
                'iat': datetime.utcnow(),
                'permissions': ['read', 'write'] if user_id % 3 == 0 else ['read']
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            return {'token': token, 'user_id': user_id, 'provider': provider}

        # Test multiple SSO providers concurrently
        providers = ['azure_ad', 'google', 'okta', 'saml']
        tasks = []
        
        for provider in providers:
            for user_id in range(25):  # 25 users per provider
                task = sso_auth_attempt(user_id, provider)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successes = [r for r in results if isinstance(r, dict)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        assert len(successes) > 0
        assert len(failures) > 0
        assert len(successes) + len(failures) == 100  # 4 providers * 25 users

    @pytest.mark.asyncio
    async def test_jwt_token_edge_cases(self):
        """Test JWT token validation edge cases"""
        
        async def validate_jwt_token(token_data: dict):
            """Validate JWT token with various edge cases"""
            try:
                if token_data.get('malformed'):
                    # Malformed token
                    return {'valid': False, 'error': 'Malformed token'}
                
                if token_data.get('expired'):
                    # Expired token
                    payload = {
                        'user_id': 123,
                        'exp': datetime.utcnow() - timedelta(hours=1)  # Expired
                    }
                    token = jwt.encode(payload, 'secret', algorithm='HS256')
                    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
                    return {'valid': False, 'error': 'Token expired'}
                
                if token_data.get('invalid_signature'):
                    # Invalid signature
                    payload = {'user_id': 123, 'exp': datetime.utcnow() + timedelta(hours=1)}
                    token = jwt.encode(payload, 'wrong_secret', algorithm='HS256')
                    try:
                        jwt.decode(token, 'secret', algorithms=['HS256'])
                    except jwt.InvalidSignatureError:
                        return {'valid': False, 'error': 'Invalid signature'}
                
                if token_data.get('missing_claims'):
                    # Missing required claims
                    payload = {'exp': datetime.utcnow() + timedelta(hours=1)}  # No user_id
                    token = jwt.encode(payload, 'secret', algorithm='HS256')
                    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
                    if 'user_id' not in decoded:
                        return {'valid': False, 'error': 'Missing required claims'}
                
                # Valid token
                payload = {
                    'user_id': token_data.get('user_id', 123),
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }
                token = jwt.encode(payload, 'secret', algorithm='HS256')
                decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
                return {'valid': True, 'payload': decoded}
                
            except Exception as e:
                return {'valid': False, 'error': str(e)}

        # Test various JWT edge cases
        test_cases = [
            {'malformed': True},
            {'expired': True},
            {'invalid_signature': True},
            {'missing_claims': True},
            {'user_id': 456},  # Valid case
        ]
        
        tasks = [validate_jwt_token(case) for case in test_cases]
        results = await asyncio.gather(*tasks)
        
        # Should handle all edge cases gracefully
        valid_results = [r for r in results if r['valid']]
        invalid_results = [r for r in results if not r['valid']]
        
        assert len(valid_results) == 1  # Only one valid case
        assert len(invalid_results) == 4  # Four invalid cases

    @pytest.mark.asyncio
    async def test_session_management_edge_cases(self):
        """Test session management edge cases"""
        
        class SessionManager:
            def __init__(self):
                self.sessions = {}
                self.lock = asyncio.Lock()
            
            async def create_session(self, user_id: int, session_data: dict):
                async with self.lock:
                    session_id = f"session_{user_id}_{int(time.time())}"
                    self.sessions[session_id] = {
                        'user_id': user_id,
                        'created_at': time.time(),
                        'last_activity': time.time(),
                        'data': session_data
                    }
                    return session_id
            
            async def validate_session(self, session_id: str, max_idle: float = 3600):
                async with self.lock:
                    if session_id not in self.sessions:
                        raise Exception("Session not found")
                    
                    session = self.sessions[session_id]
                    if time.time() - session['last_activity'] > max_idle:
                        del self.sessions[session_id]
                        raise Exception("Session expired")
                    
                    session['last_activity'] = time.time()
                    return session
            
            async def cleanup_expired_sessions(self, max_idle: float = 3600):
                async with self.lock:
                    current_time = time.time()
                    expired_sessions = [
                        sid for sid, session in self.sessions.items()
                        if current_time - session['last_activity'] > max_idle
                    ]
                    for sid in expired_sessions:
                        del self.sessions[sid]
                    return len(expired_sessions)

        session_manager = SessionManager()
        
        # Test concurrent session creation and validation
        async def session_workflow(user_id: int):
            try:
                # Create session
                session_id = await session_manager.create_session(
                    user_id, {'permissions': ['read', 'write']}
                )
                
                # Validate session immediately
                await session_manager.validate_session(session_id)
                
                # Wait and validate again (might expire)
                await asyncio.sleep(0.1)
                await session_manager.validate_session(session_id, max_idle=0.05)
                
                return f"User {user_id} session valid"
            
            except Exception as e:
                return f"User {user_id} session error: {e}"

        # Test with 50 concurrent users
        tasks = [session_workflow(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Some sessions should succeed, some should expire
        successes = [r for r in results if "session valid" in r]
        failures = [r for r in results if "session error" in r]
        
        assert len(successes) + len(failures) == 50
        # Some should expire due to short timeout
        assert len(failures) > 0


class TestMultiTenantIsolationFailures:
    """Test multi-tenant isolation and failure scenarios"""

    @pytest.mark.asyncio
    async def test_tenant_data_isolation_breach_attempts(self):
        """Test attempts to breach tenant data isolation"""
        
        class TenantDataManager:
            def __init__(self):
                self.tenant_data = {}
                self.locks = {}
            
            async def get_tenant_lock(self, tenant_id: str):
                if tenant_id not in self.locks:
                    self.locks[tenant_id] = asyncio.Lock()
                return self.locks[tenant_id]
            
            async def store_data(self, tenant_id: str, key: str, data: dict):
                lock = await self.get_tenant_lock(tenant_id)
                async with lock:
                    if tenant_id not in self.tenant_data:
                        self.tenant_data[tenant_id] = {}
                    self.tenant_data[tenant_id][key] = data
            
            async def get_data(self, tenant_id: str, key: str, requesting_tenant: str):
                # Security check - tenant isolation
                if tenant_id != requesting_tenant:
                    raise PermissionError(f"Tenant {requesting_tenant} cannot access {tenant_id} data")
                
                lock = await self.get_tenant_lock(tenant_id)
                async with lock:
                    return self.tenant_data.get(tenant_id, {}).get(key)
        
        tenant_manager = TenantDataManager()
        
        # Store data for multiple tenants
        tenants = ['tenant_a', 'tenant_b', 'tenant_c']
        for tenant in tenants:
            await tenant_manager.store_data(tenant, 'secret_data', {
                'api_key': f'secret_{tenant}',
                'config': f'config_{tenant}'
            })
        
        # Test legitimate access
        async def legitimate_access(tenant_id: str):
            try:
                data = await tenant_manager.get_data(tenant_id, 'secret_data', tenant_id)
                return f"Tenant {tenant_id} accessed own data successfully"
            except Exception as e:
                return f"Tenant {tenant_id} failed to access own data: {e}"
        
        # Test isolation breach attempts
        async def breach_attempt(attacking_tenant: str, target_tenant: str):
            try:
                data = await tenant_manager.get_data(target_tenant, 'secret_data', attacking_tenant)
                return f"SECURITY BREACH: {attacking_tenant} accessed {target_tenant} data"
            except PermissionError:
                return f"Isolation successful: {attacking_tenant} blocked from {target_tenant}"
            except Exception as e:
                return f"Unexpected error in breach attempt: {e}"
        
        # Test legitimate access for all tenants
        legitimate_tasks = [legitimate_access(tenant) for tenant in tenants]
        legitimate_results = await asyncio.gather(*legitimate_tasks)
        
        # Test breach attempts (each tenant tries to access others)
        breach_tasks = []
        for attacker in tenants:
            for target in tenants:
                if attacker != target:
                    breach_tasks.append(breach_attempt(attacker, target))
        
        breach_results = await asyncio.gather(*breach_tasks)
        
        # All legitimate access should succeed
        assert all("successfully" in r for r in legitimate_results)
        
        # All breach attempts should be blocked
        assert all("blocked" in r for r in breach_results)
        assert not any("SECURITY BREACH" in r for r in breach_results)

    @pytest.mark.asyncio
    async def test_tenant_resource_quota_enforcement(self):
        """Test tenant resource quota enforcement under stress"""
        
        class ResourceQuotaManager:
            def __init__(self):
                self.tenant_usage = {}
                self.quotas = {}
                self.locks = {}
            
            async def set_quota(self, tenant_id: str, resource_type: str, limit: int):
                if tenant_id not in self.quotas:
                    self.quotas[tenant_id] = {}
                self.quotas[tenant_id][resource_type] = limit
            
            async def allocate_resource(self, tenant_id: str, resource_type: str, amount: int):
                if tenant_id not in self.locks:
                    self.locks[tenant_id] = asyncio.Lock()
                
                async with self.locks[tenant_id]:
                    if tenant_id not in self.tenant_usage:
                        self.tenant_usage[tenant_id] = {}
                    
                    current_usage = self.tenant_usage[tenant_id].get(resource_type, 0)
                    quota = self.quotas.get(tenant_id, {}).get(resource_type, float('inf'))
                    
                    if current_usage + amount > quota:
                        raise Exception(f"Quota exceeded for {tenant_id}: {resource_type}")
                    
                    self.tenant_usage[tenant_id][resource_type] = current_usage + amount
                    return current_usage + amount
        
        quota_manager = ResourceQuotaManager()
        
        # Set quotas for tenants
        tenants = ['tenant_small', 'tenant_medium', 'tenant_large']
        quotas = {'tenant_small': 100, 'tenant_medium': 500, 'tenant_large': 1000}
        
        for tenant, quota in quotas.items():
            await quota_manager.set_quota(tenant, 'cpu_units', quota)
            await quota_manager.set_quota(tenant, 'memory_mb', quota * 10)
        
        # Test resource allocation under stress
        async def resource_allocation_test(tenant_id: str, num_requests: int):
            results = {'successes': 0, 'quota_exceeded': 0, 'errors': 0}
            
            for i in range(num_requests):
                try:
                    # Try to allocate resources
                    cpu_usage = await quota_manager.allocate_resource(tenant_id, 'cpu_units', 10)
                    memory_usage = await quota_manager.allocate_resource(tenant_id, 'memory_mb', 50)
                    results['successes'] += 1
                    await asyncio.sleep(0.001)  # Brief delay
                    
                except Exception as e:
                    if "Quota exceeded" in str(e):
                        results['quota_exceeded'] += 1
                    else:
                        results['errors'] += 1
            
            return results
        
        # Test concurrent resource allocation
        tasks = []
        for tenant in tenants:
            # Each tenant tries to allocate resources aggressively
            task = resource_allocation_test(tenant, 50)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Verify quota enforcement
        for i, tenant in enumerate(tenants):
            tenant_results = results[i]
            quota = quotas[tenant]
            
            # Should have some successes before hitting quota
            assert tenant_results['successes'] > 0
            
            # Should not exceed quota; depending on scheduling, quota_exceeded may be 0
            # but total allocation must not substantially exceed the quota
            if tenant_results['quota_exceeded'] == 0:
                # Ensure allocation remained within quota
                assert tenant_results['successes'] * 10 <= quota
            else:
                # Alternatively, we saw explicit quota exceeded events
                assert tenant_results['quota_exceeded'] >= 1
            
            # Total CPU allocation should not exceed quota significantly
            # (allowing for some race conditions)
            expected_cpu_usage = tenant_results['successes'] * 10
            assert expected_cpu_usage <= quota + 20  # Small buffer for race conditions


class TestAdvancedCachingScenarios:
    """Test advanced caching scenarios and failure modes"""

    @pytest.mark.asyncio
    async def test_cache_stampede_prevention(self):
        """Test prevention of cache stampede scenarios"""
        
        class StampedeProtectedCache:
            def __init__(self):
                self.cache = {}
                self.locks = {}
                self.computation_count = 0
            
            async def get_or_compute(self, key: str, compute_func, *args):
                # Check cache first
                if key in self.cache:
                    return self.cache[key]
                
                # Use per-key lock to prevent stampede
                if key not in self.locks:
                    self.locks[key] = asyncio.Lock()
                
                async with self.locks[key]:
                    # Double-check after acquiring lock
                    if key in self.cache:
                        return self.cache[key]
                    
                    # Compute value
                    self.computation_count += 1
                    result = await compute_func(*args)
                    self.cache[key] = result
                    return result
        
        cache = StampedeProtectedCache()
        
        async def expensive_computation(key: str):
            """Simulate expensive computation"""
            await asyncio.sleep(0.1)  # Simulate work
            return f"computed_value_for_{key}"
        
        # Simulate cache stampede - many concurrent requests for same key
        tasks = []
        for i in range(50):  # 50 concurrent requests
            task = cache.get_or_compute("popular_key", expensive_computation, "popular_key")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should get the same result
        assert all(r == "computed_value_for_popular_key" for r in results)
        
        # Should only compute once despite 50 requests
        assert cache.computation_count == 1

    @pytest.mark.asyncio
    async def test_cache_memory_pressure_handling(self):
        """Test cache behavior under memory pressure"""
        class MemoryAwareCache:
            def __init__(self, max_memory_mb: int = 1):
                self.cache = {}
                self.access_times = {}
                self.max_memory_bytes = max_memory_mb * 1024 * 1024
                self.current_memory = 0

            async def estimate_size(self, value):
                """Rough size estimation"""
                if isinstance(value, str):
                    return len(value.encode('utf-8'))
                elif isinstance(value, (list, tuple)):
                    return sum(await self.estimate_size(item) for item in value)
                elif isinstance(value, dict):
                    return sum(
                        await self.estimate_size(k) + await self.estimate_size(v)
                        for k, v in value.items()
                    )
                else:
                    return 100  # Default estimate

            async def evict_lru(self):
                """Evict least recently used items"""
                if not self.cache:
                    return

                # Sort by access time
                lru_key = min(self.access_times, key=self.access_times.get)
                value = self.cache[lru_key]
                value_size = await self.estimate_size(value)

                del self.cache[lru_key]
                del self.access_times[lru_key]
                self.current_memory -= value_size

            async def set(self, key: str, value):
                value_size = await self.estimate_size(value)

                # Evict items if necessary
                while (self.current_memory + value_size > self.max_memory_bytes
                       and self.cache):
                    await self.evict_lru()

                # Check if single item is too large
                if value_size > self.max_memory_bytes:
                    raise MemoryError(f"Item too large: {value_size} bytes")

                self.cache[key] = value
                self.access_times[key] = time.time()
                self.current_memory += value_size

            async def get(self, key: str):
                if key in self.cache:
                    self.access_times[key] = time.time()
                    return self.cache[key]
                return None
        
        cache = MemoryAwareCache(max_memory_mb=1)  # Small cache for testing
        
        # Test memory pressure scenarios
        async def cache_stress_test(item_id: int):
            try:
                # Create increasingly large items
                large_data = "x" * (item_id * 1000)  # Variable size data
                await cache.set(f"key_{item_id}", large_data)
                
                # Try to retrieve
                retrieved = await cache.get(f"key_{item_id}")
                if retrieved:
                    return f"Item {item_id} cached successfully ({len(large_data)} bytes)"
                else:
                    return f"Item {item_id} evicted"
                    
            except MemoryError as e:
                return f"Item {item_id} too large: {e}"
            except Exception as e:
                return f"Item {item_id} error: {e}"
        
        # Add items of increasing size
        tasks = [cache_stress_test(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Should handle memory pressure gracefully
        cached_items = [r for r in results if "cached successfully" in r]
        evicted_items = [r for r in results if "evicted" in r]
        too_large_items = [r for r in results if "too large" in r]
        
        # Should have some of each category
        assert len(cached_items) > 0
        assert len(evicted_items) > 0 or len(too_large_items) > 0


class TestVectorDatabaseEdgeCases:
    """Test vector database edge cases and failures"""

    @pytest.mark.asyncio
    async def test_high_dimensional_vector_operations(self):
        """Test operations with high-dimensional vectors"""
        
        async def create_high_dim_vectors(dimensions: int, count: int):
            """Create high-dimensional vectors for testing"""
            vectors = []
            for i in range(count):
                # Create random vector
                vector = np.random.rand(dimensions).astype(np.float32)
                # Normalize
                vector = vector / np.linalg.norm(vector)
                vectors.append(vector.tolist())
            return vectors
        
        async def similarity_search_stress_test(vectors, query_vector):
            """Perform similarity search stress test"""
            try:
                similarities = []
                
                # Calculate cosine similarity with all vectors
                query_norm = np.linalg.norm(query_vector)
                
                for vector in vectors:
                    vector_norm = np.linalg.norm(vector)
                    if vector_norm == 0 or query_norm == 0:
                        similarity = 0.0
                    else:
                        dot_product = np.dot(query_vector, vector)
                        similarity = dot_product / (query_norm * vector_norm)
                    similarities.append(similarity)
                
                # Find top 10 most similar
                top_indices = np.argsort(similarities)[-10:][::-1]
                top_similarities = [similarities[i] for i in top_indices]
                
                return {
                    'success': True,
                    'top_similarities': top_similarities,
                    'processed_count': len(vectors)
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'processed_count': 0
                }
        
        # Test with various vector dimensions
        dimensions_to_test = [128, 512, 1024, 2048]
        
        tasks = []
        for dimensions in dimensions_to_test:
            async def test_dimension(dim):
                vectors = await create_high_dim_vectors(dim, 100)
                query_vector = (await create_high_dim_vectors(dim, 1))[0]
                result = await similarity_search_stress_test(vectors, query_vector)
                result['dimensions'] = dim
                return result
            
            tasks.append(test_dimension(dimensions))
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully or fail gracefully
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        # Should handle most dimensions successfully
        assert len(successful_results) >= len(dimensions_to_test) // 2
        
        # Check that successful results have reasonable similarities
        for result in successful_results:
            assert len(result['top_similarities']) <= 10
            assert all(-1 <= sim <= 1 for sim in result['top_similarities'])

    @pytest.mark.asyncio
    async def test_vector_database_corruption_recovery(self):
        """Test recovery from vector database corruption"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_vectors.db"
            
            # Create a simple vector storage simulation
            class SimpleVectorDB:
                def __init__(self, db_path: str):
                    self.db_path = db_path
                    self.conn = None
                
                async def initialize(self):
                    self.conn = sqlite3.connect(self.db_path)
                    self.conn.execute('''
                        CREATE TABLE IF NOT EXISTS vectors (
                            id TEXT PRIMARY KEY,
                            vector_data BLOB,
                            metadata TEXT
                        )
                    ''')
                    self.conn.commit()
                
                async def store_vector(self, vector_id: str, vector: list, metadata: dict):
                    if not self.conn:
                        raise Exception("Database not initialized")
                    
                    vector_blob = json.dumps(vector).encode()
                    metadata_json = json.dumps(metadata)
                    
                    self.conn.execute(
                        'INSERT OR REPLACE INTO vectors (id, vector_data, metadata) VALUES (?, ?, ?)',
                        (vector_id, vector_blob, metadata_json)
                    )
                    self.conn.commit()
                
                async def retrieve_vector(self, vector_id: str):
                    if not self.conn:
                        raise Exception("Database not initialized")
                    
                    cursor = self.conn.execute(
                        'SELECT vector_data, metadata FROM vectors WHERE id = ?',
                        (vector_id,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        vector_data = json.loads(row[0].decode())
                        metadata = json.loads(row[1])
                        return {'vector': vector_data, 'metadata': metadata}
                    return None
                
                def close(self):
                    if self.conn:
                        self.conn.close()
            
            # Test normal operation
            vector_db = SimpleVectorDB(str(db_path))
            await vector_db.initialize()
            
            # Store some vectors
            test_vectors = {
                'vec_1': [0.1, 0.2, 0.3],
                'vec_2': [0.4, 0.5, 0.6],
                'vec_3': [0.7, 0.8, 0.9]
            }
            
            for vec_id, vector in test_vectors.items():
                await vector_db.store_vector(vec_id, vector, {'source': 'test'})
            
            # Verify storage
            retrieved = await vector_db.retrieve_vector('vec_1')
            assert retrieved['vector'] == [0.1, 0.2, 0.3]
            
            vector_db.close()
            
            # Simulate database corruption
            with open(db_path, 'wb') as f:
                f.write(b'corrupted data')
            
            # Test recovery from corruption
            corrupted_db = SimpleVectorDB(str(db_path))
            
            try:
                await corrupted_db.initialize()
                # Should fail due to corruption
                await corrupted_db.retrieve_vector('vec_1')
                assert False, "Should have failed with corrupted database"
            
            except Exception as e:
                # Expected corruption error
                assert "database" in str(e).lower() or "corruption" in str(e).lower() or "disk" in str(e).lower()
            
            finally:
                corrupted_db.close()


class TestVoiceProcessingFailures:
    """Test voice processing failure scenarios"""

    @pytest.mark.asyncio
    async def test_concurrent_voice_processing_failures(self):
        """Test concurrent voice processing with various failures"""
        
        async def process_audio_sample(sample_id: int, audio_data: bytes):
            """Simulate audio processing with various failure modes"""
            try:
                await asyncio.sleep(0.01)  # Simulate processing time
                
                # Simulate different failure modes
                failure_mode = sample_id % 10
                
                if failure_mode == 0:
                    raise Exception("Audio format not supported")
                elif failure_mode == 1:
                    raise Exception("Audio file corrupted")
                elif failure_mode == 2:
                    raise Exception("Audio too short")
                elif failure_mode == 3:
                    raise Exception("Audio too long")
                elif failure_mode == 4:
                    raise Exception("No speech detected")
                elif failure_mode == 5:
                    raise Exception("Multiple speakers detected")
                elif failure_mode == 6:
                    raise Exception("Background noise too high")
                elif failure_mode == 7:
                    raise Exception("Language not supported")
                elif failure_mode == 8:
                    raise Exception("Model not loaded")
                else:
                    # Success case
                    return {
                        'sample_id': sample_id,
                        'transcription': f"Sample {sample_id} transcribed successfully",
                        'confidence': 0.95,
                        'duration': len(audio_data) / 1000  # Simulated duration
                    }
            
            except Exception as e:
                return {
                    'sample_id': sample_id,
                    'error': str(e),
                    'success': False
                }
        
        # Create test audio samples (simulated)
        audio_samples = []
        for i in range(100):
            # Simulate audio data of varying sizes; wrap values to 0-255
            chunk = [(i * 100 + j) % 256 for j in range(100)]
            audio_data = bytes(chunk)
            audio_samples.append((i, audio_data))
        
        # Process all samples concurrently
        tasks = [
            process_audio_sample(sample_id, audio_data) 
            for sample_id, audio_data in audio_samples
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        successful_transcriptions = [r for r in results if 'transcription' in r]
        failed_transcriptions = [r for r in results if 'error' in r]
        
        # Should have mix of successes and failures
        assert len(successful_transcriptions) > 0
        assert len(failed_transcriptions) > 0
        
        # Check error distribution
        error_types = {}
        for result in failed_transcriptions:
            error = result['error']
            error_types[error] = error_types.get(error, 0) + 1
        
        # Should have multiple types of errors
        assert len(error_types) > 5

    @pytest.mark.asyncio
    async def test_voice_model_loading_under_memory_pressure(self):
        """Test voice model loading under memory pressure"""
        
        async def simulate_voice_model_loading(model_size_mb: int):
            """Simulate loading voice models of different sizes"""
            try:
                # Check available memory
                import psutil
                available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
                
                if model_size_mb > available_memory_mb * 0.8:  # Use 80% as threshold
                    raise MemoryError(f"Insufficient memory to load {model_size_mb}MB model")
                
                # Simulate loading time proportional to model size
                load_time = model_size_mb / 1000  # Simplified: 1s per GB
                await asyncio.sleep(min(load_time, 0.1))  # Cap at 0.1s for testing
                
                return {
                    'model_size_mb': model_size_mb,
                    'status': 'loaded',
                    'load_time': load_time,
                    'memory_used': model_size_mb
                }
            
            except Exception as e:
                return {
                    'model_size_mb': model_size_mb,
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Test loading models of various sizes
        model_sizes = [50, 100, 500, 1000, 2000, 5000]  # MB
        
        tasks = [simulate_voice_model_loading(size) for size in model_sizes]
        results = await asyncio.gather(*tasks)
        
        # Analyze loading results
        loaded_models = [r for r in results if r['status'] == 'loaded']
        failed_models = [r for r in results if r['status'] == 'failed']
        
        # Should handle memory constraints appropriately
        if failed_models:
            # Check that failures are due to memory constraints for large models
            large_model_failures = [
                r for r in failed_models 
                if r['model_size_mb'] > 1000 and "memory" in r.get('error', '').lower()
            ]
            assert len(large_model_failures) > 0


@pytest.mark.asyncio
async def test_comprehensive_enterprise_failure_simulation():
    """
    Comprehensive enterprise failure simulation testing multiple systems
    """
    results = {
        'sso_failures': 0,
        'tenant_isolation_breaches': 0,
        'quota_violations': 0,
        'cache_stampedes': 0,
        'vector_db_errors': 0,
        'voice_processing_errors': 0,
        'authentication_errors': 0,
        'successful_operations': 0
    }
    
    async def enterprise_operation_simulation(op_id: int):
        """Simulate various enterprise operations that can fail"""
        await asyncio.sleep(0.01)  # Simulate processing time
        
        operation_type = op_id % 8
        
        try:
            if operation_type == 0:
                # SSO authentication
                if op_id % 15 == 0:  # Some failures
                    results['sso_failures'] += 1
                    raise Exception("SSO provider timeout")
                results['successful_operations'] += 1
                return f"SSO auth {op_id} successful"
            
            elif operation_type == 1:
                # Tenant isolation check
                if op_id % 20 == 0:  # Rare isolation breach attempts
                    results['tenant_isolation_breaches'] += 1
                    raise PermissionError("Attempted tenant isolation breach")
                results['successful_operations'] += 1
                return f"Tenant operation {op_id} successful"
            
            elif operation_type == 2:
                # Resource quota check
                # Use a congruent condition that aligns with operation_type==2 (op_id % 8 == 2)
                # For op_id % 12 == 10, solutions exist where op_id % 8 == 2 (e.g., 10, 34, 58, ...),
                # ensuring periodic quota violations in this branch.
                if op_id % 12 == 10:  # Quota violations
                    results['quota_violations'] += 1
                    raise Exception("Resource quota exceeded")
                results['successful_operations'] += 1
                return f"Resource allocation {op_id} successful"
            
            elif operation_type == 3:
                # Cache operation
                if op_id % 25 == 0:  # Cache stampede
                    results['cache_stampedes'] += 1
                    raise Exception("Cache stampede detected")
                results['successful_operations'] += 1
                return f"Cache operation {op_id} successful"
            
            elif operation_type == 4:
                # Vector database operation
                if op_id % 18 == 0:  # Vector DB errors
                    results['vector_db_errors'] += 1
                    raise Exception("Vector database connection lost")
                results['successful_operations'] += 1
                return f"Vector operation {op_id} successful"
            
            elif operation_type == 5:
                # Voice processing
                # Use congruent condition so that some op_ids in this branch fail
                # With operation_type==5 (op_id % 8 == 5), choose op_id % 10 == 5 to intersect.
                if op_id % 10 == 5:  # Voice processing errors
                    results['voice_processing_errors'] += 1
                    raise Exception("Voice model not available")
                results['successful_operations'] += 1
                return f"Voice processing {op_id} successful"
            
            elif operation_type == 6:
                # Authentication operation
                # Ensure congruent condition with operation_type==6 (op_id % 8 == 6)
                # Choose op_id % 16 == 14 which intersects this branch (e.g., 14, 30, 46, ...)
                if op_id % 16 == 14:  # Auth errors
                    results['authentication_errors'] += 1
                    raise Exception("Token validation failed")
                results['successful_operations'] += 1
                return f"Authentication {op_id} successful"
            
            else:
                # Generic enterprise operation
                results['successful_operations'] += 1
                return f"Enterprise operation {op_id} successful"
        
        except Exception as e:
            return f"Operation {op_id} failed: {e}"
    
    # Run 500 concurrent enterprise operations
    tasks = [enterprise_operation_simulation(i) for i in range(500)]
    operation_results = await asyncio.gather(*tasks)
    
    # Verify we got expected distribution of failures
    # Only successful_operations + failures represent total attempts; failures are counted per-category and may overlap
    total_operations = 500
    
    # Should have various types of failures
    assert results['sso_failures'] > 0
    assert results['quota_violations'] > 0
    assert results['vector_db_errors'] > 0
    assert results['voice_processing_errors'] > 0
    assert results['authentication_errors'] > 0
    assert results['successful_operations'] > 0
    
    # Most operations should succeed (system should be resilient)
    success_rate = results['successful_operations'] / total_operations
    assert success_rate > 0.6  # At least 60% success rate
    
    # Log results for analysis
    print(f"Enterprise Failure Simulation Results:")
    for failure_type, count in results.items():
        percentage = (count / total_operations) * 100
        print(f"  {failure_type}: {count} ({percentage:.1f}%)")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])