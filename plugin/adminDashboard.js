// Enterprise Admin Dashboard Component
// Comprehensive administrative interface for enterprise features

class EnterpriseAdminDashboard {
    constructor(plugin) {
        this.plugin = plugin;
        this.backendClient = plugin.backendClient;
        this.dashboardData = null;
        this.refreshInterval = null;
        this.currentView = 'overview';
    }

    async createDashboard(containerEl) {
        try {
            containerEl.empty();
            
            // Create dashboard header
            this.createDashboardHeader(containerEl);
            
            // Create navigation tabs
            this.createNavigationTabs(containerEl);
            
            // Create content area
            const contentEl = containerEl.createEl('div', { cls: 'enterprise-dashboard-content' });
            
            // Load and display initial view
            await this.loadDashboardData();
            this.renderCurrentView(contentEl);
            
            // Start auto-refresh
            this.startAutoRefresh();
            
        } catch (error) {
            console.error('Failed to create admin dashboard:', error);
            this.showError(containerEl, 'Failed to load admin dashboard', error);
        }
    }

    createDashboardHeader(containerEl) {
        const headerEl = containerEl.createEl('div', { cls: 'enterprise-dashboard-header' });
        
        const titleEl = headerEl.createEl('h2', { 
            text: 'Enterprise Admin Dashboard',
            cls: 'dashboard-title'
        });
        
        const statusEl = headerEl.createEl('div', { cls: 'dashboard-status' });
        statusEl.createEl('span', { 
            text: 'Enterprise Edition',
            cls: 'status-badge enterprise'
        });
        
        const lastUpdatedEl = headerEl.createEl('div', { cls: 'last-updated' });
        lastUpdatedEl.createEl('span', { text: 'Last updated: ' });
        lastUpdatedEl.createEl('span', { 
            cls: 'timestamp',
            text: new Date().toLocaleString()
        });
    }

    createNavigationTabs(containerEl) {
        const navEl = containerEl.createEl('div', { cls: 'dashboard-navigation' });
        
        const tabs = [
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'users', label: 'User Management', icon: '👥' },
            { id: 'tenants', label: 'Tenant Management', icon: '🏢' },
            { id: 'security', label: 'Security', icon: '🛡️' },
            { id: 'compliance', label: 'Compliance', icon: '📋' },
            { id: 'monitoring', label: 'Monitoring', icon: '📈' }
        ];
        
        tabs.forEach(tab => {
            const tabEl = navEl.createEl('button', { 
                cls: `nav-tab ${this.currentView === tab.id ? 'active' : ''}`,
                text: `${tab.icon} ${tab.label}`
            });
            
            tabEl.addEventListener('click', () => {
                this.switchView(tab.id, containerEl);
            });
        });
    }

    async loadDashboardData() {
        try {
            const response = await this.backendClient.request('/admin/dashboard', {
                method: 'GET'
            });
            
            if (response.ok) {
                this.dashboardData = response.data;
            } else {
                throw new Error(response.message || 'Failed to load dashboard data');
            }
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            throw error;
        }
    }

    async switchView(viewId, containerEl) {
        this.currentView = viewId;
        
        // Update navigation
        const navTabs = containerEl.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => tab.removeClass('active'));
        
        const activeTab = Array.from(navTabs).find(tab => 
            tab.textContent.toLowerCase().includes(viewId.toLowerCase())
        );
        if (activeTab) activeTab.addClass('active');
        
        // Update content
        const contentEl = containerEl.querySelector('.enterprise-dashboard-content');
        if (contentEl) {
            await this.renderCurrentView(contentEl);
        }
    }

    async renderCurrentView(contentEl) {
        contentEl.empty();
        
        switch (this.currentView) {
            case 'overview':
                await this.renderOverview(contentEl);
                break;
            case 'users':
                await this.renderUserManagement(contentEl);
                break;
            case 'tenants':
                await this.renderTenantManagement(contentEl);
                break;
            case 'security':
                await this.renderSecurityDashboard(contentEl);
                break;
            case 'compliance':
                await this.renderComplianceDashboard(contentEl);
                break;
            case 'monitoring':
                await this.renderMonitoring(contentEl);
                break;
            default:
                await this.renderOverview(contentEl);
        }
    }

    async renderOverview(contentEl) {
        const overviewEl = contentEl.createEl('div', { cls: 'dashboard-overview' });
        
        if (!this.dashboardData) {
            overviewEl.createEl('p', { text: 'Loading dashboard data...' });
            return;
        }
        
        // Key Metrics Cards
        const metricsEl = overviewEl.createEl('div', { cls: 'metrics-grid' });
        
        const metrics = [
            {
                title: 'Total Users',
                value: this.dashboardData.users?.total_users || 0,
                change: '+12%',
                positive: true
            },
            {
                title: 'Active Tenants',
                value: this.dashboardData.tenants?.active_tenants || 0,
                change: '+8%',
                positive: true
            },
            {
                title: 'System Uptime',
                value: `${this.dashboardData.system?.uptime_percentage || 99.9}%`,
                change: 'Target: 99.9%',
                positive: true
            },
            {
                title: 'Security Score',
                value: `${Math.round(this.dashboardData.security?.vulnerability_scan_score || 8.5)}/10`,
                change: 'Excellent',
                positive: true
            }
        ];
        
        metrics.forEach(metric => {
            const cardEl = metricsEl.createEl('div', { cls: 'metric-card' });
            cardEl.createEl('h3', { text: metric.title, cls: 'metric-title' });
            cardEl.createEl('div', { text: metric.value, cls: 'metric-value' });
            cardEl.createEl('div', { 
                text: metric.change, 
                cls: `metric-change ${metric.positive ? 'positive' : 'negative'}`
            });
        });
        
        // Recent Activity
        const activityEl = overviewEl.createEl('div', { cls: 'recent-activity' });
        activityEl.createEl('h3', { text: 'Recent Activity', cls: 'section-title' });
        
        const activities = [
            '🔐 New user login: user123@company.com',
            '🏢 Tenant created: Enterprise Corp',
            '📊 Weekly compliance report generated',
            '🛡️ Security scan completed - No issues found',
            '👥 Bulk user import completed (25 users)'
        ];
        
        const activityList = activityEl.createEl('ul', { cls: 'activity-list' });
        activities.forEach(activity => {
            activityList.createEl('li', { text: activity });
        });
        
        // System Health
        const healthEl = overviewEl.createEl('div', { cls: 'system-health' });
        healthEl.createEl('h3', { text: 'System Health', cls: 'section-title' });
        
        const healthItems = [
            { name: 'API Response Time', status: 'healthy', value: '245ms' },
            { name: 'Database Performance', status: 'healthy', value: 'Optimal' },
            { name: 'Cache Hit Rate', status: 'healthy', value: '89%' },
            { name: 'Error Rate', status: 'healthy', value: '0.15%' }
        ];
        
        const healthList = healthEl.createEl('div', { cls: 'health-list' });
        healthItems.forEach(item => {
            const itemEl = healthList.createEl('div', { cls: 'health-item' });
            itemEl.createEl('span', { text: item.name, cls: 'health-name' });
            itemEl.createEl('span', { 
                text: item.value, 
                cls: `health-status ${item.status}`
            });
        });
    }

    async renderUserManagement(contentEl) {
        const userMgmtEl = contentEl.createEl('div', { cls: 'user-management' });
        
        // Header with actions
        const headerEl = userMgmtEl.createEl('div', { cls: 'management-header' });
        headerEl.createEl('h3', { text: 'User Management', cls: 'section-title' });
        
        const actionsEl = headerEl.createEl('div', { cls: 'header-actions' });
        
        const addUserBtn = actionsEl.createEl('button', { 
            text: '+ Add User',
            cls: 'btn btn-primary'
        });
        addUserBtn.addEventListener('click', () => this.showAddUserDialog());
        
        const bulkActionsBtn = actionsEl.createEl('button', { 
            text: 'Bulk Actions',
            cls: 'btn btn-secondary'
        });
        bulkActionsBtn.addEventListener('click', () => this.showBulkActionsDialog());
        
        // User filters
        const filtersEl = userMgmtEl.createEl('div', { cls: 'user-filters' });
        
        const searchInput = filtersEl.createEl('input', { 
            type: 'text',
            placeholder: 'Search users...',
            cls: 'search-input'
        });
        
        const roleFilter = filtersEl.createEl('select', { cls: 'role-filter' });
        roleFilter.createEl('option', { value: '', text: 'All Roles' });
        roleFilter.createEl('option', { value: 'admin', text: 'Admin' });
        roleFilter.createEl('option', { value: 'user', text: 'User' });
        roleFilter.createEl('option', { value: 'analyst', text: 'Analyst' });
        
        const statusFilter = filtersEl.createEl('select', { cls: 'status-filter' });
        statusFilter.createEl('option', { value: '', text: 'All Status' });
        statusFilter.createEl('option', { value: 'active', text: 'Active' });
        statusFilter.createEl('option', { value: 'inactive', text: 'Inactive' });
        
        // User table
        try {
            const usersResponse = await this.backendClient.request('/admin/users', {
                method: 'GET'
            });
            
            if (usersResponse.ok) {
                this.renderUserTable(userMgmtEl, usersResponse.data.users);
            } else {
                throw new Error('Failed to load users');
            }
        } catch (error) {
            console.error('Failed to load users:', error);
            userMgmtEl.createEl('p', { 
                text: 'Failed to load user data',
                cls: 'error-message'
            });
        }
    }

    renderUserTable(containerEl, users) {
        const tableContainer = containerEl.createEl('div', { cls: 'table-container' });
        const table = tableContainer.createEl('table', { cls: 'user-table' });
        
        // Table header
        const thead = table.createEl('thead');
        const headerRow = thead.createEl('tr');
        
        const headers = ['Select', 'Email', 'Tenant', 'Roles', 'Status', 'Last Login', 'Actions'];
        headers.forEach(header => {
            headerRow.createEl('th', { text: header });
        });
        
        // Table body
        const tbody = table.createEl('tbody');
        
        users.forEach(user => {
            const row = tbody.createEl('tr');
            
            // Checkbox
            const checkboxCell = row.createEl('td');
            const checkbox = checkboxCell.createEl('input', { type: 'checkbox' });
            checkbox.value = user.user_id;
            
            // Email
            row.createEl('td', { text: user.email });
            
            // Tenant
            row.createEl('td', { text: user.tenant_id });
            
            // Roles
            const rolesCell = row.createEl('td');
            user.roles.forEach(role => {
                rolesCell.createEl('span', { 
                    text: role,
                    cls: 'role-badge'
                });
            });
            
            // Status
            const statusCell = row.createEl('td');
            statusCell.createEl('span', { 
                text: user.status,
                cls: `status-badge ${user.status}`
            });
            
            // Last Login
            row.createEl('td', { 
                text: user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'
            });
            
            // Actions
            const actionsCell = row.createEl('td');
            const editBtn = actionsCell.createEl('button', { 
                text: 'Edit',
                cls: 'btn btn-small'
            });
            editBtn.addEventListener('click', () => this.editUser(user));
            
            const deleteBtn = actionsCell.createEl('button', { 
                text: 'Delete',
                cls: 'btn btn-small btn-danger'
            });
            deleteBtn.addEventListener('click', () => this.deleteUser(user));
        });
    }

    async renderTenantManagement(contentEl) {
        const tenantMgmtEl = contentEl.createEl('div', { cls: 'tenant-management' });
        
        // Header
        const headerEl = tenantMgmtEl.createEl('div', { cls: 'management-header' });
        headerEl.createEl('h3', { text: 'Tenant Management', cls: 'section-title' });
        
        const addTenantBtn = headerEl.createEl('button', { 
            text: '+ Add Tenant',
            cls: 'btn btn-primary'
        });
        addTenantBtn.addEventListener('click', () => this.showAddTenantDialog());
        
        // Load and display tenants
        try {
            const tenantsResponse = await this.backendClient.request('/admin/tenants', {
                method: 'GET'
            });
            
            if (tenantsResponse.ok) {
                this.renderTenantGrid(tenantMgmtEl, tenantsResponse.data.tenants);
            } else {
                throw new Error('Failed to load tenants');
            }
        } catch (error) {
            console.error('Failed to load tenants:', error);
            tenantMgmtEl.createEl('p', { 
                text: 'Failed to load tenant data',
                cls: 'error-message'
            });
        }
    }

    renderTenantGrid(containerEl, tenants) {
        const gridEl = containerEl.createEl('div', { cls: 'tenant-grid' });
        
        tenants.forEach(tenant => {
            const cardEl = gridEl.createEl('div', { cls: 'tenant-card' });
            
            // Tenant header
            const headerEl = cardEl.createEl('div', { cls: 'tenant-header' });
            headerEl.createEl('h4', { text: tenant.name });
            headerEl.createEl('span', { 
                text: tenant.tier.toUpperCase(),
                cls: `tier-badge ${tenant.tier}`
            });
            
            // Tenant stats
            const statsEl = cardEl.createEl('div', { cls: 'tenant-stats' });
            
            const stats = [
                { label: 'Users', value: tenant.user_count },
                { label: 'Storage', value: `${tenant.storage_used_gb}GB` },
                { label: 'API Calls', value: tenant.api_calls_30d },
                { label: 'Revenue', value: `$${tenant.monthly_cost}` }
            ];
            
            stats.forEach(stat => {
                const statEl = statsEl.createEl('div', { cls: 'stat' });
                statEl.createEl('span', { text: stat.label, cls: 'stat-label' });
                statEl.createEl('span', { text: stat.value, cls: 'stat-value' });
            });
            
            // Actions
            const actionsEl = cardEl.createEl('div', { cls: 'tenant-actions' });
            
            const manageBtn = actionsEl.createEl('button', { 
                text: 'Manage',
                cls: 'btn btn-small'
            });
            manageBtn.addEventListener('click', () => this.manageTenant(tenant));
            
            const settingsBtn = actionsEl.createEl('button', { 
                text: 'Settings',
                cls: 'btn btn-small'
            });
            settingsBtn.addEventListener('click', () => this.showTenantSettings(tenant));
        });
    }

    async renderSecurityDashboard(contentEl) {
        const securityEl = contentEl.createEl('div', { cls: 'security-dashboard' });
        
        securityEl.createEl('h3', { text: 'Security Dashboard', cls: 'section-title' });
        
        try {
            const securityResponse = await this.backendClient.request('/admin/security', {
                method: 'GET'
            });
            
            if (securityResponse.ok) {
                const securityData = securityResponse.data;
                
                // Security metrics
                const metricsEl = securityEl.createEl('div', { cls: 'security-metrics' });
                
                const metrics = [
                    { name: 'Security Incidents (30d)', value: securityData.incidents.metrics.monthly_incident_count },
                    { name: 'Critical Incidents', value: securityData.incidents.metrics.critical_incident_count },
                    { name: 'Avg Resolution Time', value: `${Math.round(securityData.incidents.metrics.avg_resolution_time_hours)}h` },
                    { name: 'Overdue Reviews', value: securityData.access_controls.overdue_reviews }
                ];
                
                metrics.forEach(metric => {
                    const metricEl = metricsEl.createEl('div', { cls: 'security-metric' });
                    metricEl.createEl('h4', { text: metric.name });
                    metricEl.createEl('span', { text: metric.value, cls: 'metric-value' });
                });
                
                // Recent incidents
                const incidentsEl = securityEl.createEl('div', { cls: 'recent-incidents' });
                incidentsEl.createEl('h4', { text: 'Recent Security Incidents' });
                
                const incidentsList = incidentsEl.createEl('div', { cls: 'incidents-list' });
                
                securityData.incidents.recent_incidents.forEach(incident => {
                    const incidentEl = incidentsList.createEl('div', { cls: 'incident-item' });
                    incidentEl.createEl('span', { text: incident.title });
                    incidentEl.createEl('span', { 
                        text: incident.severity,
                        cls: `severity-badge ${incident.severity}`
                    });
                    incidentEl.createEl('span', { 
                        text: new Date(incident.reported_at).toLocaleDateString()
                    });
                });
                
            } else {
                throw new Error('Failed to load security data');
            }
        } catch (error) {
            console.error('Failed to load security dashboard:', error);
            securityEl.createEl('p', { 
                text: 'Failed to load security data',
                cls: 'error-message'
            });
        }
    }

    async renderComplianceDashboard(contentEl) {
        const complianceEl = contentEl.createEl('div', { cls: 'compliance-dashboard' });
        
        complianceEl.createEl('h3', { text: 'Compliance Dashboard', cls: 'section-title' });
        
        try {
            const complianceResponse = await this.backendClient.request('/admin/compliance', {
                method: 'GET'
            });
            
            if (complianceResponse.ok) {
                const complianceData = complianceResponse.data;
                
                // Compliance scores
                const scoresEl = complianceEl.createEl('div', { cls: 'compliance-scores' });
                
                const gdprScore = complianceEl.createEl('div', { cls: 'compliance-score gdpr' });
                gdprScore.createEl('h4', { text: 'GDPR Compliance' });
                gdprScore.createEl('div', { text: '✓ Compliant', cls: 'score-status compliant' });
                gdprScore.createEl('p', { text: `${complianceData.gdpr.processing_activities} processing activities documented` });
                
                const soc2Score = complianceEl.createEl('div', { cls: 'compliance-score soc2' });
                soc2Score.createEl('h4', { text: 'SOC2 Compliance' });
                const soc2ScoreValue = Math.round(complianceData.soc2.compliance_score);
                soc2Score.createEl('div', { 
                    text: `${soc2ScoreValue}%`, 
                    cls: `score-status ${soc2ScoreValue >= 90 ? 'compliant' : 'warning'}`
                });
                soc2Score.createEl('p', { text: `${complianceData.soc2.controls.effective_controls}/${complianceData.soc2.controls.total_controls} controls effective` });
                
                // Compliance actions
                const actionsEl = complianceEl.createEl('div', { cls: 'compliance-actions' });
                actionsEl.createEl('h4', { text: 'Required Actions' });
                
                const actionsList = actionsEl.createEl('ul', { cls: 'actions-list' });
                complianceData.recommendations.forEach(recommendation => {
                    actionsList.createEl('li', { text: recommendation });
                });
                
            } else {
                throw new Error('Failed to load compliance data');
            }
        } catch (error) {
            console.error('Failed to load compliance dashboard:', error);
            complianceEl.createEl('p', { 
                text: 'Failed to load compliance data',
                cls: 'error-message'
            });
        }
    }

    async renderMonitoring(contentEl) {
        const monitoringEl = contentEl.createEl('div', { cls: 'monitoring-dashboard' });
        
        monitoringEl.createEl('h3', { text: 'System Monitoring', cls: 'section-title' });
        
        // Real-time metrics
        const metricsEl = monitoringEl.createEl('div', { cls: 'monitoring-metrics' });
        
        if (this.dashboardData && this.dashboardData.system) {
            const systemData = this.dashboardData.system;
            
            const metrics = [
                { name: 'CPU Usage', value: `${systemData.cpu_usage_percentage}%`, status: 'healthy' },
                { name: 'Memory Usage', value: `${systemData.memory_usage_percentage}%`, status: 'healthy' },
                { name: 'Disk Usage', value: `${systemData.disk_usage_percentage}%`, status: 'healthy' },
                { name: 'Active Connections', value: systemData.active_connections, status: 'healthy' }
            ];
            
            metrics.forEach(metric => {
                const metricEl = metricsEl.createEl('div', { cls: 'monitoring-metric' });
                metricEl.createEl('h4', { text: metric.name });
                metricEl.createEl('span', { 
                    text: metric.value,
                    cls: `metric-value ${metric.status}`
                });
            });
        }
        
        // Performance chart placeholder
        const chartEl = monitoringEl.createEl('div', { cls: 'performance-chart' });
        chartEl.createEl('h4', { text: 'Performance Trends' });
        chartEl.createEl('div', { 
            text: 'Performance chart would be displayed here',
            cls: 'chart-placeholder'
        });
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(async () => {
            try {
                await this.loadDashboardData();
                const contentEl = document.querySelector('.enterprise-dashboard-content');
                if (contentEl) {
                    await this.renderCurrentView(contentEl);
                }
                
                // Update timestamp
                const timestampEl = document.querySelector('.timestamp');
                if (timestampEl) {
                    timestampEl.textContent = new Date().toLocaleString();
                }
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, 30000); // Refresh every 30 seconds
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }

    // Dialog and action methods
    showAddUserDialog() {
        // Implementation for add user dialog
        console.log('Add user dialog would be shown');
    }

    showBulkActionsDialog() {
        // Implementation for bulk actions dialog
        console.log('Bulk actions dialog would be shown');
    }

    editUser(user) {
        console.log('Edit user:', user);
    }

    deleteUser(user) {
        console.log('Delete user:', user);
    }

    showAddTenantDialog() {
        console.log('Add tenant dialog would be shown');
    }

    manageTenant(tenant) {
        console.log('Manage tenant:', tenant);
    }

    showTenantSettings(tenant) {
        console.log('Tenant settings:', tenant);
    }

    showError(containerEl, message, error) {
        containerEl.empty();
        const errorEl = containerEl.createEl('div', { cls: 'dashboard-error' });
        errorEl.createEl('h3', { text: 'Error Loading Dashboard' });
        errorEl.createEl('p', { text: message });
        if (error) {
            errorEl.createEl('pre', { text: error.toString() });
        }
    }
}

module.exports = EnterpriseAdminDashboard;