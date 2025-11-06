import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

const ToastContext = createContext(null);

let idCounter = 1;

function ToastContainer({ toasts, remove }) {
  return (
    <div className="fixed right-6 bottom-6 z-50 space-y-3">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`max-w-sm w-full px-4 py-3 rounded shadow-lg text-sm flex justify-between items-start gap-4 ${
            t.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' :
            t.type === 'error' ? 'bg-red-50 border border-red-200 text-red-800' :
            'bg-gray-50 border border-gray-200 text-gray-800'
          }`}
        >
          <div className="flex-1">
            <div className="font-medium">{t.title}</div>
            <div className="mt-1 text-sm">{t.message}</div>
          </div>
          <div className="ml-4 flex-shrink-0">
            <button onClick={() => remove(t.id)} className="text-xs text-gray-600 hover:text-gray-800">×</button>
          </div>
        </div>
      ))}
    </div>
  );
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => {
    setToasts(t => t.filter(x => x.id !== id));
  }, []);

  const push = useCallback(({ type = 'info', title = '', message = '', ttl = 5000 }) => {
    const id = idCounter++;
    setToasts(t => [{ id, type, title, message }, ...t]);
    if (ttl > 0) {
      setTimeout(() => remove(id), ttl);
    }
    return id;
  }, [remove]);

  const api = {
    success: (message, title = 'Success', ttl) => push({ type: 'success', title, message, ttl }),
    error: (message, title = 'Error', ttl) => push({ type: 'error', title, message, ttl }),
    info: (message, title = 'Info', ttl) => push({ type: 'info', title, message, ttl }),
    remove
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <ToastContainer toasts={toasts} remove={remove} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return ctx;
}

export default ToastProvider;
