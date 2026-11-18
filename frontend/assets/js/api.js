/**
 * OutbreakWatch & Ebola Screening System API Client
 * Ministry of Health, The Gambia
 */

// Dynamically resolve base URL to match whether the frontend is loaded on localhost, 127.0.0.1, or a LAN IP
function getInitialApiBase() {
    if (typeof window !== 'undefined' && window.API_BASE_URL) {
        return window.API_BASE_URL;
    }
    const host = (typeof window !== 'undefined' && window.location && window.location.hostname) 
        ? window.location.hostname 
        : '127.0.0.1';
    
    // Default to the same hostname that served the frontend
    const targetHost = (host === 'localhost' || host === '127.0.0.1') ? host : '127.0.0.1';
    return `http://${targetHost}:8000/api/v1`;
}

const API_CONFIG = {
    BASE_URL: getInitialApiBase(),
    TIMEOUT_MS: 15000
};

const OutbreakAPI = {
    async request(endpoint, options = {}) {
        let currentBase = API_CONFIG.BASE_URL;
        const token = this.getAuthToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...(options.headers || {})
        };

        const executeFetch = async (baseUrl) => {
            const url = `${baseUrl}${endpoint}`;
            const response = await fetch(url, { ...options, headers });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: HTTP ${response.status}`);
            }
            return await response.json();
        };

        try {
            return await executeFetch(currentBase);
        } catch (firstErr) {
            // If connection failed (e.g. host mismatch between 127.0.0.1 and localhost), try the alternate address
            if (currentBase.includes('127.0.0.1:8000') || currentBase.includes('localhost:8000')) {
                const alternateBase = currentBase.includes('127.0.0.1:8000')
                    ? currentBase.replace('127.0.0.1:8000', 'localhost:8000')
                    : currentBase.replace('localhost:8000', '127.0.0.1:8000');
                
                try {
                    const result = await executeFetch(alternateBase);
                    // Cache the successful base URL for all future requests
                    API_CONFIG.BASE_URL = alternateBase;
                    window.API_BASE_URL = alternateBase;
                    return result;
                } catch (secondErr) {
                    console.error(`API Connection failed on both interfaces for [${endpoint}]:`, firstErr, secondErr);
                    throw new Error("Unable to connect to the OutbreakWatch backend. Please verify the Python API server is running (run: cd backend; python main.py).");
                }
            }
            throw firstErr;
        }
    },

    // --------------------------------------------------------------------------
    // AUTHENTICATION & ACCESS CONTROL
    // --------------------------------------------------------------------------
    async loginAdmin(email, password) {
        const res = await this.request('/auth/admin-login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        localStorage.setItem('ebola_auth_token', res.access_token);
        localStorage.setItem('ebola_auth_user', JSON.stringify(res.user));
        return res;
    },

    async loginStaff(email, password) {
        const res = await this.request('/auth/staff-login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        localStorage.setItem('ebola_auth_token', res.access_token);
        localStorage.setItem('ebola_auth_user', JSON.stringify(res.user));
        return res;
    },

    getAuthToken() {
        return localStorage.getItem('ebola_auth_token') || null;
    },

    getCurrentUser() {
        const u = localStorage.getItem('ebola_auth_user');
        return u ? JSON.parse(u) : null;
    },

    logout(redirectUrl = 'login.html') {
        localStorage.removeItem('ebola_auth_token');
        localStorage.removeItem('ebola_auth_user');
        window.location.href = redirectUrl;
    },

    async getRoles() {
        return this.request('/auth/roles');
    },

    async listUsers() {
        return this.request('/auth/users');
    },

    async createUser(payload) {
        return this.request('/auth/users', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async deleteUser(userId) {
        return this.request(`/auth/users/${encodeURIComponent(userId)}`, {
            method: 'DELETE'
        });
    },

    async getAuditLogs() {
        return this.request('/auth/audit-logs');
    },

    // --------------------------------------------------------------------------
    // PHASE 1 & 2: TRAVELLER DECLARATION & QR
    // --------------------------------------------------------------------------
    async submitTravellerDeclaration(payload) {
        return this.request('/submissions', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async getSubmissionConfirmation(referenceCode) {
        return this.request(`/submissions/${encodeURIComponent(referenceCode)}/confirmation`);
    },

    // --------------------------------------------------------------------------
    // PHASE 3: AIRPORT QR VERIFICATION
    // --------------------------------------------------------------------------
    async verifyQRToken(tokenOrRef) {
        return this.request(`/qr/verify/${encodeURIComponent(tokenOrRef)}`);
    },

    // --------------------------------------------------------------------------
    // PHASE 4: AUTHORITY DASHBOARD & CASE WORKFLOW
    // --------------------------------------------------------------------------
    async getStaffDashboard() {
        return this.request('/staff/dashboard');
    },

    async getStaffSubmissions(filters = {}) {
        const params = new URLSearchParams();
        if (filters.risk_category) params.append('risk_category', filters.risk_category);
        if (filters.status) params.append('status', filters.status);
        if (filters.flight_number) params.append('flight_number', filters.flight_number);
        const query = params.toString() ? `?${params.toString()}` : '';
        return this.request(`/staff/submissions${query}`);
    },

    async getStaffSubmissionDetails(submissionId) {
        return this.request(`/staff/submissions/${encodeURIComponent(submissionId)}`);
    },

    async recordOfficerAssessment(submissionId, payload) {
        return this.request(`/staff/submissions/${encodeURIComponent(submissionId)}/assessment`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async revokeQRCode(submissionId, reason = 'Administrative revocation') {
        return this.request(`/staff/submissions/${encodeURIComponent(submissionId)}/revoke-qr?reason=${encodeURIComponent(reason)}`, {
            method: 'POST'
        });
    },

    // --------------------------------------------------------------------------
    // OUTBREAK AREA MANAGEMENT & DYNAMIC RULES
    // --------------------------------------------------------------------------
    async getOutbreakAreas() {
        return this.request('/admin/outbreak-areas');
    },

    async addOutbreakArea(payload) {
        return this.request('/admin/outbreak-areas', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async updateOutbreakArea(areaId, payload) {
        return this.request(`/admin/outbreak-areas/${encodeURIComponent(areaId)}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },

    async deleteOutbreakArea(areaId) {
        return this.request(`/admin/outbreak-areas/${encodeURIComponent(areaId)}`, {
            method: 'DELETE'
        });
    },

    async getOutbreaks(status = null) {
        const query = status ? `?status=${encodeURIComponent(status)}` : '';
        return this.request(`/outbreaks/${query}`);
    },

    async getSurveillanceSummary() {
        return this.request('/analytics/summary');
    }
};

window.OutbreakAPI = OutbreakAPI;
