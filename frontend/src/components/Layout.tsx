import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Home, PlusCircle, Settings, FileText, Bell, LogOut } from 'lucide-react';
import { logout } from '../services/authService';
import { useQuery } from '@tanstack/react-query';
import { getAnomalies } from '../services/alertService';

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { data: anomalies } = useQuery({
    queryKey: ['all-anomalies'],
    queryFn: getAnomalies,
    refetchInterval: 60000, // Refetch every minute
  });

  const unacknowledgedCritical = anomalies?.filter(a => a.severity === 'critical' && a.status === 'active').length || 0;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'Onboarding', path: '/onboarding', icon: PlusCircle },
    { name: 'Vet Report', path: '/vet-report', icon: FileText },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col w-full text-slate-900">
      <header className="bg-white border-b border-slate-200 py-4 px-6 flex justify-between items-center sticky top-0 z-10 w-full">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">P</span>
          </div>
          <h1 className="text-xl font-bold text-slate-800">PawPulse</h1>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 text-slate-500 hover:text-violet-600 relative">
            <Bell size={20} />
            {unacknowledgedCritical > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center border-2 border-white">
                {unacknowledgedCritical}
              </span>
            )}
          </button>
          <div className="w-10 h-10 bg-slate-200 rounded-full overflow-hidden border border-slate-300">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" />
          </div>
          <button 
            onClick={handleLogout}
            className="p-2 text-slate-500 hover:text-red-600"
            title="Logout"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <div className="flex flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <aside className="w-64 hidden md:block pr-8">
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-violet-50 text-violet-700'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Icon size={18} />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="flex-1">
          <Outlet />
        </main>
      </div>

      {/* Mobile Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 flex justify-around py-3 px-2 z-10">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center gap-1 transition-colors ${
                isActive ? 'text-violet-700' : 'text-slate-500'
              }`}
            >
              <Icon size={20} />
              <span className="text-[10px]">{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default Layout;
