/**
 * Customer details page with logs and complaints.
 */
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  fetchCustomerDetails,
  fetchCustomerComplaints,
  createLog,
  fetchLogs,
  updateComplaintStatus
} from '../services/api';
import { getCurrentUserRole } from '../services/auth';
import { useToast } from './ToastProvider';

export default function CustomerDetails() {
  const { id } = useParams();
  const [customer, setCustomer] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [logFilterType, setLogFilterType] = useState('');
  const [logSearchTerm, setLogSearchTerm] = useState('');
  const [currentRole, setCurrentRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showLogForm, setShowLogForm] = useState(false);
  const [logData, setLogData] = useState({
    type: 'CALL',
    description: ''
  });
  const toast = useToast();

  useEffect(() => {
    loadCustomerData();
  }, [id]);

  useEffect(() => {
    loadLogs();
  }, [id]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const role = await getCurrentUserRole();
        if (mounted) setCurrentRole(role);
      } catch (err) {
        console.warn('Failed to detect role', err);
      }
    })();
    return () => { mounted = false; };
  }, []);

  async function loadCustomerData() {
    try {
      setLoading(true);
      const [customerData, complaintsData] = await Promise.all([
        fetchCustomerDetails(id),
        fetchCustomerComplaints(id)
      ]);
      setCustomer(customerData);
      setComplaints(complaintsData);
      // clear any previous error state
      // but prefer using toast for user-visible errors
    } catch (err) {
      toast.error(err.message || 'Failed to load customer');
    } finally {
      setLoading(false);
    }
  }

  async function loadLogs() {
    try {
      setLogsLoading(true);
      const data = await fetchLogs(id);
      setLogs(data);
    } catch (err) {
      // non-fatal for logs
      console.warn('Failed to load logs', err);
    } finally {
      setLogsLoading(false);
    }
  }

  async function handleCreateLog(e) {
    e.preventDefault();
    try {
      await createLog({
        ...logData,
        customerId: id
      });
      setShowLogForm(false);
      setLogData({ type: 'CALL', description: '' });
      // Optionally refresh customer data
      await Promise.all([loadCustomerData(), loadLogs()]);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleChangeComplaintStatus(complaintId, newStatus) {
    try {
      const updated = await updateComplaintStatus(complaintId, { status: newStatus });
      // update local state
      setComplaints(prev => prev.map(c => c.id === complaintId ? { ...c, ...updated } : c));
    } catch (err) {
      if (err.status === 403) {
        toast.error('You do not have permission to change the complaint status.');
      } else {
        toast.error(err.message || 'Failed to update complaint');
      }
    }
  }

  if (loading) return <div className="flex justify-center p-8">Loading...</div>;
  if (error) return <div className="text-red-600 p-4">{error}</div>;
  if (!customer) return <div className="p-4">Customer not found</div>;

  return (
    <div className="container mx-auto p-4">
      {/* Customer Info */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
      if (!customer) return <div className="p-4">Customer not found</div>;
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-600">Email</p>
            <p>{customer.email}</p>
          </div>
          <div>
            <p className="text-gray-600">Phone</p>
            <p>{customer.phone}</p>
          </div>
          <div className="col-span-2">
            <p className="text-gray-600">Address</p>
            <p>{customer.address}</p>
          </div>
        </div>
      </div>

      {/* Create Log Button/Form */}
      <div className="mb-6">
        {!showLogForm ? (
          <button
            onClick={() => setShowLogForm(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Log Entry
          </button>
        ) : (
          <form onSubmit={handleCreateLog} className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">New Log Entry</h3>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Type</label>
              <select
                value={logData.type}
                onChange={(e) => setLogData({...logData, type: e.target.value})}
                className="w-full p-2 border rounded"
              >
                <option value="CALL">Call</option>
                <option value="EMAIL">Email</option>
                <option value="MEETING">Meeting</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Description</label>
              <textarea
                value={logData.description}
                onChange={(e) => setLogData({...logData, description: e.target.value})}
                className="w-full p-2 border rounded"
                rows="3"
                required
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowLogForm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Create Log
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Complaints List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Complaints</h2>
        {complaints.length === 0 ? (
          <p className="text-gray-500">No complaints found.</p>
        ) : (
          <div className="space-y-4">
            {complaints.map(complaint => (
              <div key={complaint.id} className="border-b pb-4">
                <div className="flex justify-between items-start">
                  <h3 className="font-medium">{complaint.title}</h3>
                  <div className="flex items-center gap-2">
                    {(currentRole === 'admin' || currentRole === 'manager') ? (
                      <select
                        value={complaint.status}
                        onChange={(e) => handleChangeComplaintStatus(complaint.id, e.target.value)}
                        className="px-2 py-1 rounded border bg-white text-sm"
                        title="Change complaint status"
                      >
                        <option value="OPEN">OPEN</option>
                        <option value="IN_PROGRESS">IN_PROGRESS</option>
                        <option value="RESOLVED">RESOLVED</option>
                      </select>
                    ) : (
                      <span className={`px-2 py-1 rounded text-sm ${
                        complaint.status === 'OPEN' ? 'bg-red-100 text-red-800' :
                        complaint.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {complaint.status}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-gray-600 mt-2">{complaint.description}</p>
                {complaint.attachmentUrl && (
                  <a
                    href={complaint.attachmentUrl}
                    className="text-blue-500 hover:underline text-sm mt-2 block"
                  >
                    View Attachment
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Logs List & Filters */}
      <div className="bg-white shadow rounded-lg p-6 mt-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Interaction Logs</h2>
          <div className="flex items-center gap-2">
            <select
              value={logFilterType}
              onChange={(e) => setLogFilterType(e.target.value)}
              className="p-2 border rounded"
            >
              <option value="">All Types</option>
              <option value="CALL">Call</option>
              <option value="EMAIL">Email</option>
              <option value="MEETING">Meeting</option>
            </select>
            <input
              placeholder="Search logs..."
              value={logSearchTerm}
              onChange={(e) => setLogSearchTerm(e.target.value)}
              className="p-2 border rounded"
            />
            <button onClick={() => loadLogs()} className="px-3 py-2 bg-gray-100 rounded">Refresh</button>
          </div>
        </div>

        {logsLoading ? (
          <div>Loading logs...</div>
        ) : (
          <div className="space-y-4">
            {logs
              .filter(l => !logFilterType || l.type === logFilterType)
              .filter(l => !logSearchTerm || (l.description || '').toLowerCase().includes(logSearchTerm.toLowerCase()))
              .map(log => (
                <div key={log.id} className="border-b pb-3">
                  <div className="flex justify-between">
                    <div>
                      <div className="text-sm text-gray-600">{log.type}</div>
                      <div className="font-medium">{log.description}</div>
                    </div>
                    <div className="text-sm text-gray-500">{new Date(log.createdAt || Date.now()).toLocaleString()}</div>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}