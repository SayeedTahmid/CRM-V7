/**
 * Customer list component with search and filtering.
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchCustomers } from '../services/api';

export default function CustomerList() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadCustomers() {
    try {
      setLoading(true);
      const data = await fetchCustomers();
      setCustomers(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const filteredCustomers = customers.filter(customer => 
    customer.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div className="flex justify-center p-8">Loading...</div>;
  if (error) return <div className="text-red-600 p-4">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Customers</h1>
        <input
          type="text"
          placeholder="Search customers..."
          className="px-4 py-2 border rounded-lg"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredCustomers.map(customer => (
          <Link
            key={customer.id}
            to={`/customers/${customer.id}`}
            className="block p-6 border rounded-lg hover:shadow-lg transition-shadow"
          >
            <h2 className="text-xl font-semibold">{customer.companyName}</h2>
            <p className="text-gray-600">{customer.email}</p>
            <p className="text-gray-500 text-sm">{customer.phone}</p>
          </Link>
        ))}
      </div>

      {filteredCustomers.length === 0 && (
        <p className="text-center text-gray-500 mt-8">
          No customers found.
        </p>
      )}
    </div>
  );
}