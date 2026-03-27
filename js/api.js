// js/api.js
const API_BASE = 'http://localhost:8000/api/v1';

// Token store/retrieve
function setToken(token) {
    localStorage.setItem('token', token);
}

function getToken() {
    return localStorage.getItem('token');
}

// Main API caller
async function apiCall(endpoint, method = 'GET', data = null, isFormData = false) {
    const url = `${API_BASE}${endpoint}`;
    
    const headers = {};
    if (!isFormData) {
        headers['Content-Type'] = 'application/json';
    }
    
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method,
        headers,
    };
    
    if (data) {
        if (isFormData) {
            options.body = data;
        } else {
            options.body = JSON.stringify(data);
        }
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (response.status === 401) {
            alert('Session expired. Please login again.');
            window.location.href = 'login.html';
            return;
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}