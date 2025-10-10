// Enterprise Authentication Component
// Handles SSO login flows, JWT token management, and multi-tenant authentication

class EnterpriseAuth { constructor(plugin) { this.plugin = plugin;
        this.backendClient = plugin.backendClient;
        this.currentUser = null;
        this.currentTenant = null;
        this.authToken = null;
        this.refreshToken = null;
        this.tokenExpiry = null;
        this.refreshTimer = null;
    }

    async initialize() { try {
            // Check for stored authentication
            await this.loadStoredAuth();

            // Validate existing token if present
            if(this.authToken) { const isValid = await this.validateToken();
                if(!isValid) { await this.clearAuth();
                }
            }

            // Start token refresh timer if authenticated
            if(this.authToken) { this.startTokenRefresh();
            }

        } catch(error) { console.error('Failed to initialize enterprise auth:', error);
            await this.clearAuth();
        }
    }

    async loadStoredAuth() { try { const storedAuth = localStorage.getItem('enterprise_auth');
            if(storedAuth) { const authData = JSON.parse(storedAuth);

                this.authToken = authData.access_token;
                this.refreshToken = authData.refresh_token;
                this.tokenExpiry = new Date(authData.expires_at);
                this.currentUser = authData.user;
                this.currentTenant = authData.tenant;

                // Update backend client with token
                this.backendClient.setAuthToken(this.authToken);
            }
        } catch(error) { console.error('Failed to load stored auth:', error);
        }
    }

    async saveAuth(authData) { try { const authStorage = { access_token: authData.access_token,
                refresh_token: authData.refresh_token,
                expires_at: authData.expires_at,
                user: authData.user,
                tenant: authData.tenant };

            localStorage.setItem('enterprise_auth', JSON.stringify(authStorage));

            this.authToken = authData.access_token;
            this.refreshToken = authData.refresh_token;
            this.tokenExpiry = new Date(authData.expires_at);
            this.currentUser = authData.user;
            this.currentTenant = authData.tenant;

            // Update backend client
            this.backendClient.setAuthToken(this.authToken);

        } catch(error) { console.error('Failed to save auth data:', error);
        }
    }

    async clearAuth() { try { localStorage.removeItem('enterprise_auth');

            this.authToken = null;
            this.refreshToken = null;
            this.tokenExpiry = null;
            this.currentUser = null;
            this.currentTenant = null;

            // Clear backend client token
            this.backendClient.clearAuthToken();

            // Stop refresh timer
            if(this.refreshTimer) { clearTimeout(this.refreshTimer);
                this.refreshTimer = null;
            }

        } catch(error) { console.error('Failed to clear auth:', error);
        }
    }

    async validateToken() { try { if(!this.authToken) return false;

            // Check expiry
            if(this.tokenExpiry && new Date() >= this.tokenExpiry) { return false;
            }

            // Validate with backend
            const response = await this.backendClient.request('/sso/validate', { method: 'POST',
                data: { token: this.authToken }
            });

            return response.ok && response.data.valid;

        } catch(error) { console.error('Token validation failed:', error);
            return false;
        }
    }

    async refreshAuthToken() { try { if(!this.refreshToken) { throw new Error('No refresh token available');
            }

            const response = await this.backendClient.request('/sso/refresh', { method: 'POST',
                data: { refresh_token: this.refreshToken }
            });

            if(response.ok) { await this.saveAuth({ access_token: response.data.access_token,
                    refresh_token: response.data.refresh_token || this.refreshToken,
                    expires_at: response.data.expires_at,
                    user: this.currentUser,
                    tenant: this.currentTenant });

                this.startTokenRefresh();
                return true;
            } else { throw new Error(response.message || 'Token refresh failed');
            }

        } catch(error) { console.error('Failed to refresh token:', error);
            await this.clearAuth();
            return false;
        }
    }

    startTokenRefresh() { if(this.refreshTimer) { clearTimeout(this.refreshTimer);
        }

        if(!this.tokenExpiry) return;

        // Refresh token 5 minutes before expiry
        const refreshTime = this.tokenExpiry.getTime() - Date.now() - (5 * 60 * 1000);

        if(refreshTime > 0) { this.refreshTimer = setTimeout(async() => { await this.refreshAuthToken();
            }, refreshTime);
        }
    }

    async getAvailableProviders() { try { const response = await this.backendClient.request('/sso/providers', { method: 'GET'
            });

            return response.ok ? response.data.providers : [];

        } catch(error) { console.error('Failed to get SSO providers:', error);
            return [];
        }
    }

    async initiateLogin(provider) { try { const response = await this.backendClient.request('/sso/login', { method: 'POST',
                data: { provider: provider }
            });

            if(response.ok) {
                // Open SSO login window
                const loginWindow = window.open(response.data.login_url,
                    'sso_login',
                    'width = 600, height = 700, scrollbars = yes, resizable = yes'
                );

                // Wait for login completion
                return new Promise((resolve, reject) => { const checkClosed = setInterval(() => { if(loginWindow.closed) { clearInterval(checkClosed);
                            // Check for auth callback
                            this.checkAuthCallback().then(resolve).catch(reject);
                        }
                    }, 1000);

                    // Timeout after 5 minutes
                    setTimeout(() => { clearInterval(checkClosed);
                        if(!loginWindow.closed) { loginWindow.close();
                        }
                        reject(new Error('Login timeout'));
                    }, 300000);
                });
            } else { throw new Error(response.message || 'Login initiation failed');
            }

        } catch(error) { console.error('Failed to initiate login:', error);
            throw error;
        }
    }

    async checkAuthCallback() { try {
            // Check for auth parameters in URL or storage
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');

            if(code && state) {
                // Exchange code for tokens
                const response = await this.backendClient.request('/sso/callback', { method: 'POST',
                    data: { code: code, state: state }
                });

                if(response.ok) { await this.saveAuth(response.data);
                    this.startTokenRefresh();
                    return response.data;
                } else { throw new Error(response.message || 'Authentication failed');
                }
            }

            // Check for stored temporary auth
            const tempAuth = localStorage.getItem('temp_enterprise_auth');
            if(tempAuth) { localStorage.removeItem('temp_enterprise_auth');
                const authData = JSON.parse(tempAuth);
                await this.saveAuth(authData);
                this.startTokenRefresh();
                return authData;
            }

            throw new Error('No authentication data found');

        } catch(error) { console.error('Auth callback check failed:', error);
            throw error;
        }
    }

    async logout() { try { if(this.authToken) {
                // Notify backend of logout
                await this.backendClient.request('/sso/logout', { method: 'POST',
                    data: { token: this.authToken }
                });
            }
        } catch(error) { console.error('Logout request failed:', error);
        } finally { await this.clearAuth();
        }
    }

    createLoginInterface(containerEl) { containerEl.empty();

        const loginEl = containerEl.createEl('div', { cls: 'enterprise-login' });

        // Header
        const headerEl = loginEl.createEl('div', { cls: 'login-header' });
        headerEl.createEl('h2', { text: 'Enterprise Sign In', cls: 'login-title' });
        headerEl.createEl('p', { text: 'Sign in with your organization\'s SSO provider',
            cls: 'login-subtitle'
        });

        // Login form
        const formEl = loginEl.createEl('div', { cls: 'login-form' });

        // Provider selection
        this.createProviderSelection(formEl);

        // Alternative login
        const altLoginEl = formEl.createEl('div', { cls: 'alternative-login' });
        altLoginEl.createEl('hr');
        altLoginEl.createEl('p', { text: 'Or sign in directly:' });

        const directLoginBtn = altLoginEl.createEl('button', { text: 'Direct Login',
            cls: 'btn btn-secondary'
        });
        directLoginBtn.addEventListener('click', () => this.showDirectLogin(formEl));
    }

    async createProviderSelection(containerEl) { try { const providers = await this.getAvailableProviders();

            const providerEl = containerEl.createEl('div', { cls: 'provider-selection' });
            providerEl.createEl('h3', { text: 'Select SSO Provider' });

            if(providers.length === 0) { providerEl.createEl('p', { text: 'No SSO providers configured',
                    cls: 'error-message'
                });
                return;
            }

            providers.forEach(provider => { const providerBtn = providerEl.createEl('button', { cls: `provider-btn ${ provider.name.toLowerCase()}`
                });

                // Provider icon and name
                const iconEl = providerBtn.createEl('span', { cls: `provider-icon ${ provider.name.toLowerCase()}`
                });
                iconEl.textContent = this.getProviderIcon(provider.name);

                providerBtn.createEl('span', { text: `Sign in with ${ provider.display_name }`,
                    cls: 'provider-text'
                });

                providerBtn.addEventListener('click', async() => { try { providerBtn.disabled = true;
                        providerBtn.textContent = 'Signing in...';

                        await this.initiateLogin(provider.name);

                        // On successful login, notify plugin
                        this.plugin.onAuthenticationChanged(true, this.currentUser, this.currentTenant);

                    } catch(error) { console.error('Login failed:', error);
                        providerBtn.disabled = false;
                        providerBtn.innerHTML = `<span class="provider-icon ${ provider.name.toLowerCase()}">${ this.getProviderIcon(provider.name)}</span><span class="provider-text">Sign in with ${ provider.display_name }</span>`;

                        this.showError(containerEl, 'Login failed: ' + error.message);
                    }
                });
            });

        } catch(error) { console.error('Failed to load providers:', error);
            containerEl.createEl('p', { text: 'Failed to load SSO providers',
                cls: 'error-message'
            });
        }
    }

    showDirectLogin(containerEl) { const directLoginEl = containerEl.createEl('div', { cls: 'direct-login' });

        directLoginEl.createEl('h3', { text: 'Direct Login' });

        // Email input
        const emailInput = directLoginEl.createEl('input', { type: 'email',
            placeholder: 'Email address',
            cls: 'login-input'
        });

        // Password input
        const passwordInput = directLoginEl.createEl('input', { type: 'password',
            placeholder: 'Password',
            cls: 'login-input'
        });

        // Tenant input
        const tenantInput = directLoginEl.createEl('input', { type: 'text',
            placeholder: 'Organization/Tenant ID',
            cls: 'login-input'
        });

        // Login button
        const loginBtn = directLoginEl.createEl('button', { text: 'Sign In',
            cls: 'btn btn-primary login-btn'
        });

        loginBtn.addEventListener('click', async() => { try { loginBtn.disabled = true;
                loginBtn.textContent = 'Signing in...';

                const response = await this.backendClient.request('/sso/login/direct', { method: 'POST',
                    data: { email: emailInput.value,
                        password: passwordInput.value,
                        tenant_id: tenantInput.value }
                });

                if(response.ok) { await this.saveAuth(response.data);
                    this.startTokenRefresh();

                    // Notify plugin
                    this.plugin.onAuthenticationChanged(true, this.currentUser, this.currentTenant);
                } else { throw new Error(response.message || 'Login failed');
                }

            } catch(error) { console.error('Direct login failed:', error);
                loginBtn.disabled = false;
                loginBtn.textContent = 'Sign In';

                this.showError(directLoginEl, 'Login failed: ' + error.message);
            }
        });
    }

    createUserProfile(containerEl) { if(!this.isAuthenticated()) { containerEl.createEl('p', { text: 'Not authenticated' });
            return;
        }

        const profileEl = containerEl.createEl('div', { cls: 'user-profile' });

        // User info
        const userInfoEl = profileEl.createEl('div', { cls: 'user-info' });

        const avatarEl = userInfoEl.createEl('div', { cls: 'user-avatar' });
        avatarEl.textContent = this.currentUser.email.charAt(0).toUpperCase();

        const detailsEl = userInfoEl.createEl('div', { cls: 'user-details' });
        detailsEl.createEl('h3', { text: this.currentUser.email });
        detailsEl.createEl('p', { text: this.currentTenant.name });

        // Roles
        if(this.currentUser.roles && this.currentUser.roles.length > 0) { const rolesEl = detailsEl.createEl('div', { cls: 'user-roles' });
            this.currentUser.roles.forEach(role => { rolesEl.createEl('span', { text: role,
                    cls: 'role-badge'
                });
            });
        }

        // Actions
        const actionsEl = profileEl.createEl('div', { cls: 'profile-actions' });

        const settingsBtn = actionsEl.createEl('button', { text: 'Account Settings',
            cls: 'btn btn-secondary'
        });
        settingsBtn.addEventListener('click', () => this.showAccountSettings());

        const logoutBtn = actionsEl.createEl('button', { text: 'Sign Out',
            cls: 'btn btn-danger'
        });
        logoutBtn.addEventListener('click', async() => { await this.logout();
            this.plugin.onAuthenticationChanged(false, null, null);
        });
    }

    getProviderIcon(providerName) { const icons = {
            'azure': '🏢',
            'google': '🔍',
            'okta': '🔒',
            'saml': '🔐',
            'ldap': '📁'
        };

        return icons[providerName.toLowerCase()] || '🔑';
    }

    showError(containerEl, message) { let errorEl = containerEl.querySelector('.auth-error');
        if(!errorEl) { errorEl = containerEl.createEl('div', { cls: 'auth-error' });
        }

        errorEl.empty();
        errorEl.createEl('p', { text: message });

        // Auto-hide after 5 seconds
        setTimeout(() => { if(errorEl) errorEl.remove();
        }, 5000);
    }

    showAccountSettings() {
        // Implementation for account settings
        console.log('Account settings would be shown');
    }

    isAuthenticated() { return !!(this.authToken && this.currentUser && this.currentTenant);
    }

    getCurrentUser() { return this.currentUser;
    }

    getCurrentTenant() { return this.currentTenant;
    }

    hasPermission(permission) { return this.currentUser &&
                this.currentUser.permissions &&
                this.currentUser.permissions.includes(permission);
    }

    hasRole(role) { return this.currentUser &&
                this.currentUser.roles &&
                this.currentUser.roles.includes(role);
    }

    destroy() { if(this.refreshTimer) { clearTimeout(this.refreshTimer);
        }
    }
}

module.exports = EnterpriseAuth;