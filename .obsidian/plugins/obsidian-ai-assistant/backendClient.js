class BackendClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl || 'http://localhost:8000';
        // Support passing a function as token provider directly
        if (typeof options === 'function') {
            this._tokenProvider = options;
            options = {};
        } else {
            this._tokenProvider = options.tokenProvider || null;
        }
        this.timeout = options.timeout || 30000;
        this.token = options.token || null;
        this._pollers = new Map(); // id -> interval handle
        this._nextPollerId = 1;

        // Retry configuration - only for connection errors, not AI queries
        this.retryDelay = options.retryDelay || 1000; // Delay before retry in ms

        // Endpoints that are safe to retry (non-AI, idempotent operations)
        this.retryableEndpoints = [
            '/health',
            '/status',
            '/api/health',
            '/api/status',
            '/api/config',
            '/api/performance/metrics',
            '/api/auth/verify'
        ];
    }

    setAuthToken(token) {
        this.token = token || null;
    }

    clearAuthToken() {
        this.token = null;
    }

    isAbortSignal(obj) {
        return !!(
            obj &&
            typeof obj === 'object' &&
            'aborted' in obj &&
            typeof obj.addEventListener === 'function'
        );
    }

    /**
    * Check if an endpoint is safe to retry (non-AI, idempotent)
    */
    isRetryableEndpoint(endpoint) {
        return this.retryableEndpoints.some(pattern => endpoint.includes(pattern));
    }

    /**
    * Check if an error is a connection error (not a server error response)
    */
    isConnectionError(error) {
        // Connection errors: fetch failed, timeout, network error
        // These have status 0 and an error message
        return error && error.status === 0 && error.error;
    }

    async request(method, endpoint, body = null, headers = {}, signal) {
        // Support calling as request(endpoint, options) like in some plugin code
        if (typeof method === 'string' && method.startsWith('/')) {
            // Shift args: request(endpoint, options)
            const ep = method;
            const opts = endpoint || {};
            method = (opts.method || 'GET').toUpperCase();
            body = opts.body || opts.data || null;
            headers = opts.headers || {};
            signal = opts.signal;
            endpoint = ep;
        }

        const url = this.resolveUrl(endpoint);
        const finalHeaders = Object.assign(
            {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            headers
        );
        const token = this._tokenProvider ? this._tokenProvider() : this.token;
        if (token && !finalHeaders['Authorization']) {
            finalHeaders['Authorization'] = `Bearer ${token}`;
        }

        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), this.timeout);
        try {
            const res = await fetch(url, {
                method,
                headers: finalHeaders,
                body: body ? JSON.stringify(body) : null,
                signal: signal || controller.signal,
            });
            const text = await res.text();
            let data = null;
            try {
                data = text ? JSON.parse(text) : null;
            } catch (_) {}
            return {
                ok: res.ok,
                status: res.status,
                data,
                raw: text,
                url,
            };
        } catch (error) {
            const errorResponse = { ok: false, status: 0, error: String(error), data: null };

            // Only retry connection errors on retryable endpoints
            if (this.isConnectionError(errorResponse) && this.isRetryableEndpoint(endpoint)) {
                console.log(`Backend connection failed, retrying in ${this.retryDelay}ms...`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));

                try {
                    const retryRes = await fetch(url, {
                        method,
                        headers: finalHeaders,
                        body: body ? JSON.stringify(body) : null,
                        signal: signal || controller.signal,
                    });
                    const retryText = await retryRes.text();
                    let retryData = null;
                    try {
                        retryData = retryText ? JSON.parse(retryText) : null;
                    } catch (_) {}
                    return {
                        ok: retryRes.ok,
                        status: retryRes.status,
                        data: retryData,
                        raw: retryText,
                        url,
                    };
                } catch (retryError) {
                    // Return original error if retry fails
                    return errorResponse;
                }
            }

            return errorResponse;
        } finally {
            clearTimeout(id);
        }
    }

    async get(endpoint, extra = {}) {
        // extra may be headers or AbortSignal
        let headers = {};
        let signal;
        if (this.isAbortSignal(extra)) {
            signal = extra;
        } else if (extra && typeof extra === 'object') {
            headers = extra.headers || extra;
            signal = extra.signal;
        }
        return this.request('GET', endpoint, null, headers, signal);
    }

    async post(endpoint, body = {}, extra = {}) {
        // extra may be headers or AbortSignal
        let headers = {};
        let signal;
        if (this.isAbortSignal(extra)) {
            signal = extra;
        } else if (extra && typeof extra === 'object') {
            headers = extra.headers || extra;
            signal = extra.signal;
        }
        return this.request('POST', endpoint, body, headers, signal);
    }

    startPolling(endpoint, intervalMs, onData, onError) {
        const id = this._nextPollerId++;
        const tick = async () => {
            try {
                const res = await this.get(endpoint);
                if (res && res.ok) {
                    if (typeof onData === 'function') onData(res.data);
                } else {
                    const err = new Error(`Polling failed: ${res ? res.status : 'no response'}`);
                    if (typeof onError === 'function') onError(err);
                }
            } catch (e) {
                if (typeof onError === 'function') onError(e);
            }
        };
        const handle = setInterval(tick, Math.max(1000, intervalMs || 30000));
        this._pollers.set(id, handle);
        // Fire immediately once
        tick();
        return id;
    }

    stopPolling(pollerId) {
        const handle = this._pollers.get(pollerId);
        if (handle) {
            clearInterval(handle);
            this._pollers.delete(pollerId);
        }
    }

    resolveUrl(endpoint) {
        if (!endpoint) return this.baseUrl;
        if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) return endpoint;
        const base = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
        const ep = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return `${base}${ep}`;
    }
}

module.exports = BackendClient;
