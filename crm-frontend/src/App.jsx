import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import ToastProvider from './components/ToastProvider';
import { getCurrentUserRole } from './services/auth';
import CustomerList from './components/CustomerList';
import CustomerDetails from './components/CustomerDetails';
import CreateComplaint from './components/CreateComplaint';
import LoginPage from './components/LoginPage';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState(null);

  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!user) {
        if (mounted) setRole(null);
        return;
      }
      try {
        const r = await getCurrentUserRole();
        if (mounted) setRole(r);
      } catch (err) {
        console.warn('Failed to load role', err);
      }
    })();
    return () => { mounted = false; };
  }, [user]);

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  return (
    <ToastProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
        {user && (
          <nav className="bg-white shadow">
            <div className="container mx-auto px-4 py-3">
              <div className="flex justify-between items-center">
                <h1 className="text-xl font-semibold">Codex CRM</h1>
                <div className="flex items-center gap-4">
                  <span className="text-gray-600">{user.email}</span>
                  <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                    {role ? role.toUpperCase() : 'ROLE'}
                  </span>
                  <button
                    onClick={() => getAuth().signOut()}
                    className="text-sm text-gray-600 hover:text-gray-800"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
          </nav>
        )}

        <main className="py-6">
          <Routes>
            <Route 
              path="/" 
              element={user ? <CustomerList /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/login" 
              element={!user ? <LoginPage /> : <Navigate to="/" />} 
            />
            <Route 
              path="/customers/:id" 
              element={user ? <CustomerDetails /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/customers/:id/complaints/new" 
              element={user ? <CreateComplaint /> : <Navigate to="/login" />} 
            />
          </Routes>
        </main>
        </div>
      </BrowserRouter>
    </ToastProvider>
  );
}
 
export default App;
