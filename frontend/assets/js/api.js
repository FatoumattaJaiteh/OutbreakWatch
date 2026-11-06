/**
 * OutbreakWatch & Ebola Screening System API Client
 * Ministry of Health, The Gambia
 */
const API_CONFIG = {
    BASE_URL: window.API_BASE_URL || 'http://localhost:8000/api/v1',
    TIMEOUT_MS: 15000
};

const OutbreakAPI = {
    async request(endpoint, options = {}) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        const token = this.getAuthToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, { ...options, headers });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Request failed with status ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    // --------------------------------------------------------------------------
    // AUTHENTICATION & ACCESS CONTROL (Section 4 & 14)
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
        const raw = localStorage.getItem('ebola_auth_user');
        try {
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    },

    logout(redirectPath = '../index.html') {
        localStorage.removeItem('ebola_auth_token');
        localStorage.removeItem('ebola_auth_user');
        window.location.href = redirectPath;
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

    async getOutbreakAreas() {
        return this.request('/admin/outbreak-areas');
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
