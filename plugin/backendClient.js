// Centralized Backend API Client for Obsidian AI Assistant
// Handles authentication, error handling, and retry logic

class BackendClient { constructor(baseURL, getToken) { this.baseURL = baseURL;
    this.getToken = getToken; // function to retrieve current token
    this.timeout = 30000;
    this.maxRetries = 2;
    }

    async request(endpoint, { method = 'GET', data = null, headers = {}, retry = 0, signal = null } = {}) { const url = this.baseURL + endpoint;
    const authToken = this.getToken ? this.getToken() : null;
    if(authToken) { headers['Authorization'] = `Bearer ${ authToken }`;
    }
    if(method !== 'GET') { headers['Content-Type'] = 'application/json';
    }
    try { const res = await fetch(url, { method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal,
        });
        if(!res.ok) { if(retry < this.maxRetries && [502, 503, 504].includes(res.status)) {
            // Retry on transient errors
            return this.request(endpoint, { method, data, headers, retry: retry + 1, signal });
        }
        const errorText = await res.text();
        throw new Error(`API Error: ${ res.status } ${ res.statusText } - ${ errorText }`);
        }
        return await res.json();
    } catch(err) { if(retry < this.maxRetries && err.name !== 'AbortError') {
        // Retry on network errors but not abort errors
        return this.request(endpoint, { method, data, headers, retry: retry + 1, signal });
        }
        throw err;
    }
    }

    async get(endpoint, params = null, signal = null) {
    // Optionally add query params
    let url = endpoint;
    if(params) { const query = new URLSearchParams(params).toString();
        url += '?' + query;
    }
    return this.request(url, { method: 'GET', signal });
    }

    async post(endpoint, data, signal = null) { return this.request(endpoint, { method: 'POST', data, signal });
    }

    async put(endpoint, data, signal = null) { return this.request(endpoint, { method: 'PUT', data, signal });
    }

    async delete(endpoint, signal = null) { return this.request(endpoint, { method: 'DELETE', signal });
    }

    // Utility method for polling endpoints with real-time updates
    startPolling(endpoint, intervalMs, callback, errorCallback = null) { const pollId = setInterval(async() => { try { const data = await this.get(endpoint);
        callback(data);
        } catch(error) { if(errorCallback) { errorCallback(error);
        } else { console.error('Polling error:', error);
        }
        }
    }, intervalMs);

    return pollId; // Return interval ID to allow stopping }

    stopPolling(pollId) { if(pollId) { clearInterval(pollId);
    }
    }
}

module.exports = BackendClient;
