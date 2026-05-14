import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import VoucherPage from './pages/VoucherPage';
import Home from './pages/Home';
import { Menu, CloudLightning } from 'lucide-react';

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  return (
    <div className="flex flex-col md:flex-row h-screen bg-[#020617] text-white font-sans selection:bg-blue-500/20 selection:text-blue-400">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-[#020617] border-b border-white/5 sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
            <CloudLightning className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-white tracking-tight">TallyGenius</span>
        </div>
        <button 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400"
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {/* Sidebar - Conditional for Mobile */}
      <div className={`${isMobileMenuOpen ? 'block' : 'hidden'} md:block fixed md:relative inset-0 z-40 md:z-20 w-full md:w-auto`}>
         {/* Backdrop for mobile */}
         <div 
           className="absolute inset-0 bg-black/60 md:hidden backdrop-blur-sm"
           onClick={() => setIsMobileMenuOpen(false)}
         ></div>
         <div className="relative h-full w-72 max-w-[80%] md:max-w-none shadow-2xl md:shadow-none animate-fade-in md:animate-none">
            <Sidebar />
         </div>
      </div>

      <main className="flex-1 overflow-x-hidden overflow-y-auto bg-[#0f172a] scroll-smooth">
        {children}
      </main>
    </div>
  );
};

const AppRoutes = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  if (isHomePage) {
    return (
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    );
  }

  return (
    <DashboardLayout>
      <Routes>
        <Route 
          path="/bank-xml" 
          element={
            <VoucherPage 
              title="Bank Statements" 
              description="Convert your bank statements to Tally Payment & Receipt Vouchers instantly."
              type="bank" 
            />
          } 
        />
        <Route 
          path="/sales-xml" 
          element={
            <VoucherPage 
              title="Sales Vouchers" 
              description="Process your sales invoices with smart GST handling."
              type="sales" 
            />
          } 
        />
        <Route 
          path="/purchase-xml" 
          element={
            <VoucherPage 
              title="Purchase Vouchers" 
              description="Generate accurate purchase entries into Tally XML format."
              type="purchase" 
            />
          } 
        />
        <Route 
          path="/debit-note-xml" 
          element={
            <VoucherPage 
              title="Debit Note" 
              description="Convert purchase return & debit note data into Tally Prime compatible XML."
              type="debit-note" 
            />
          } 
        />
        <Route 
          path="/credit-note-xml" 
          element={
            <VoucherPage 
              title="Credit Note" 
              description="Convert sales return & credit note data into Tally Prime compatible XML."
              type="credit-note" 
            />
          } 
        />
      </Routes>
    </DashboardLayout>
  );
};

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
