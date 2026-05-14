import { NavLink } from 'react-router-dom';
import { Building2, ShoppingCart, Truck, CloudLightning, LayoutDashboard, Zap, Home, TrendingDown, TrendingUp } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Back to Home', path: '/', icon: <Home className="w-5 h-5" /> },
    { name: 'Bank Vouchers', path: '/bank-xml', icon: <Building2 className="w-5 h-5" /> },
    { name: 'Sales Vouchers', path: '/sales-xml', icon: <ShoppingCart className="w-5 h-5" /> },
    { name: 'Purchase Vouchers', path: '/purchase-xml', icon: <Truck className="w-5 h-5" /> },
    { name: 'Debit Note', path: '/debit-note-xml', icon: <TrendingDown className="w-5 h-5" /> },
    { name: 'Credit Note', path: '/credit-note-xml', icon: <TrendingUp className="w-5 h-5" /> },
  ];

  return (
    <aside className="w-full h-full bg-[#020617] text-slate-400 flex flex-col border-r border-white/5">
      {/* Sidebar Header */}
      <div className="p-8 pb-10 flex items-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <CloudLightning className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">TallyGenius</h1>
          <p className="text-[10px] text-blue-400 font-bold tracking-[0.2em] uppercase">Enterprise AI</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-1">
        <div className="px-4 mb-4 flex items-center justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Navigation</span>
          <LayoutDashboard className="w-3.5 h-3.5 text-slate-600" />
        </div>
        
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `sidebar-item group ${isActive ? 'sidebar-active text-white' : ''} relative overflow-hidden`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`transition-all duration-300 ${isActive ? 'scale-110 text-blue-400' : 'group-hover:scale-110 group-hover:text-white'}`}>
                  {item.icon}
                </div>
                <span className="font-medium tracking-wide">{item.name}</span>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-500 rounded-r-full shadow-[0_0_15px_rgba(59,130,246,0.8)]" />
                )}
                {/* Hover Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/5 to-blue-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 pointer-events-none" />
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Sidebar Footer */}
      <div className="p-6">
        <div className="glass-card p-5 border-blue-500/20 bg-blue-500/5 relative overflow-hidden shadow-none hover:translate-y-0">
          <div className="absolute -top-10 -right-10 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl"></div>
          <div className="flex items-center gap-3 mb-3">
             <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.6)]"></div>
             <span className="text-xs font-bold text-white uppercase tracking-wider">Cloud Engine</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed font-medium">
            Connected to Tally Intelligence Sync. Ready for data processing.
          </p>
          <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
             <span className="text-[10px] text-slate-500 font-bold uppercase">v2.4.0-Stable</span>
             <Zap className="w-3 h-3 text-blue-400" />
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
