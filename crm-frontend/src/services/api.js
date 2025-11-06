/**
 * API client for CRM backend services.
 * Handles auth headers and base URL configuration.
 */
import { getAuth } from 'firebase/auth';
import { getCurrentUserTenant } from './auth';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function getAuthHeaders() {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) {
    throw new Error('User not authenticated');
  }
  const token = await user.getIdToken();
  // Prefer tenant from custom claims when available (set by backend/admin)
  const tenantFromClaims = await getCurrentUserTenant().catch(() => null);
  const tenant = tenantFromClaims || user.tenantId || 'default';

  return {
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': tenant,
    'Content-Type': 'application/json'
  };
}

export async function fetchCustomers() {
  const headers = await getAuthHeaders();
  const response = await fetch(`${BASE_URL}/v1/customers`, {
    headers
  });
  if (!response.ok) throw new Error('Failed to fetch customers');
  return response.json();
}

export async function fetchCustomerDetails(id) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${BASE_URL}/v1/customers/${id}`, {
    headers
  });
  if (!response.ok) throw new Error('Failed to fetch customer details');
  return response.json();
}

export async function createLog(data) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${BASE_URL}/v1/logs`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create log');
  return response.json();
}

export async function fetchCustomerComplaints(customerId) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${BASE_URL}/v1/complaints?customerId=${customerId}`, {
    headers
  });
  if (!response.ok) throw new Error('Failed to fetch complaints');
  return response.json();
}

export async function createComplaint(data, file) {
  const headers = await getAuthHeaders();
  delete headers['Content-Type']; // Let browser set for multipart

  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    formData.append(key, value);
  });
  if (file) {
    formData.append('file', file);
  }

  const response = await fetch(`${BASE_URL}/v1/complaints`, {
    method: 'POST',
    headers,
    body: formData
  });
  if (!response.ok) throw new Error('Failed to create complaint');
  return response.json();
}

export async function fetchLogs(customerId, params = {}) {
  const headers = await getAuthHeaders();
  const qs = new URLSearchParams({ customerId, ...params }).toString();
  const response = await fetch(`${BASE_URL}/v1/logs?${qs}`, { headers });
  if (!response.ok) throw new Error('Failed to fetch logs');
  return response.json();
}

export async function updateComplaintStatus(complaintId, patch) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${BASE_URL}/v1/complaints/${complaintId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(patch)
  });
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    const msg = text || 'Failed to update complaint';
    const err = new Error(msg);
    err.status = response.status;
    throw err;
  }
  return response.json();
}