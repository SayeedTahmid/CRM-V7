/**
 * Create complaint form with file upload.
 */
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createComplaint } from '../services/api';
import { useToast } from './ToastProvider';

export default function CreateComplaint() {
  const { id: customerId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'LOW'
  });
  const [file, setFile] = useState(null);
  const toast = useToast();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await createComplaint({
        ...formData,
        customerId
      }, file);
      toast.success('Complaint created');
      // Navigate back to customer details
      navigate(`/customers/${customerId}`);
    } catch (err) {
      setError(err.message);
      toast.error(err.message || 'Failed to create complaint');
      setLoading(false);
    }
  }

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Create New Complaint</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 mb-2">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full p-2 border rounded"
              rows="4"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 mb-2">Priority</label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({...formData, priority: e.target.value})}
              className="w-full p-2 border rounded"
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-700 mb-2">Attachment (optional)</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full"
            />
          </div>

          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate(`/customers/${customerId}`)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`px-6 py-2 rounded text-white ${
                loading ? 'bg-blue-400' : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              {loading ? 'Creating...' : 'Create Complaint'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}