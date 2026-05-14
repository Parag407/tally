import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  CloudLightning, 
  ShieldCheck, 
  Smartphone, 
  FileCheck, 
  Database, 
  Zap
} from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen bg-[#0f172a] text-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <CloudLightning className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">TallyGenius</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-slate-400 font-medium">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
        </div>
        <Link to="/bank-xml" className="btn-primary flex items-center gap-2">
          Get Started <ArrowRight className="w-4 h-4" />
        </Link>
      </nav>

      {/* Hero Section */}
      <section className="relative px-8 pt-20 pb-32 max-w-7xl mx-auto text-center overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-blue-500/10 blur-[120px] rounded-full -z-10"></div>
        <div className="absolute top-40 right-0 w-72 h-72 bg-cyan-500/10 blur-[100px] rounded-full -z-10 animate-float"></div>

        <div className="animate-fade-in space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
            <Zap className="w-4 h-4" /> Powered by Advanced AI
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-tight">
            Convert Bank Statements to <br />
            <span className="text-gradient">Tally in Seconds</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto font-medium">
            The most accurate AI-powered conversion tool for accountants. 
            Smart validation, auto error fixing, and zero manual entry.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
            <Link to="/bank-xml" className="btn-primary text-lg px-10 py-4 w-full sm:w-auto">
              Get Started for Free
            </Link>
            <button className="btn-secondary text-lg px-10 py-4 w-full sm:w-auto">
              View Demo
            </button>
          </div>
          <div className="pt-12 flex items-center justify-center gap-8 text-slate-500 grayscale opacity-50">
             <span className="font-bold">STRIPE</span>
             <span className="font-bold">RAZORPAY</span>
             <span className="font-bold">LINEAR</span>
             <span className="font-bold">NOTION</span>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-8 py-32 max-w-7xl mx-auto">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-3xl md:text-5xl font-bold">Why Choose TallyGenius?</h2>
          <p className="text-slate-400 text-lg">Built for speed, accuracy, and total data control.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: "AI Smart Mapping",
              desc: "Our AI automatically detects columns like dates, amounts, and narrations from any Excel format.",
              icon: <CloudLightning className="w-8 h-8 text-blue-400" />
            },
            {
              title: "Auto Error Fixing",
              desc: "Don't spend hours on validation. AI detects and fixes common date and number formatting errors.",
              icon: <Zap className="w-8 h-8 text-cyan-400" />
            },
            {
              title: "Instant XML Export",
              desc: "Generate Tally-ready XML files that import perfectly every time. No more reference master errors.",
              icon: <FileCheck className="w-8 h-8 text-green-400" />
            },
            {
              title: "Secure & Encrypted",
              desc: "Your data stays private. We process files on-the-fly and never store your sensitive statements.",
              icon: <ShieldCheck className="w-8 h-8 text-purple-400" />
            },
            {
              title: "Batch Processing",
              desc: "Process thousands of transactions in a single click. Scale your accounting without more staff.",
              icon: <Database className="w-8 h-8 text-pink-400" />
            },
            {
              title: "Tally Prime Ready",
              desc: "Compatible with all versions of Tally Prime and Tally.ERP 9. Full legacy support included.",
              icon: <Smartphone className="w-8 h-8 text-orange-400" />
            }
          ].map((feature, i) => (
            <div key={i} className="glass-card p-8 group">
              <div className="mb-6 p-3 rounded-2xl bg-white/5 w-fit group-hover:scale-110 transition-transform duration-300">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="px-8 py-32 bg-white/5 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-20">
            <h2 className="text-3xl md:text-5xl font-bold">How It Works</h2>
            <p className="text-slate-400 text-lg">Go from statement to Tally entry in 3 easy steps.</p>
          </div>

          <div className="flex flex-col md:flex-row items-start justify-between gap-12 relative">
             {/* Connector Line */}
             <div className="hidden md:block absolute top-10 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500/50 to-cyan-500/50 -z-0"></div>

             {[
               { step: "01", title: "Upload Excel", desc: "Drag and drop your bank statement or sales sheet." },
               { step: "02", title: "AI Validation", desc: "AI checks for errors and balances your debits/credits." },
               { step: "03", title: "Export to Tally", desc: "Download the XML and import it directly into Tally." }
             ].map((item, i) => (
               <div key={i} className="flex-1 relative z-10 space-y-6 md:text-center px-4">
                 <div className="w-20 h-20 rounded-full bg-[#0f172a] border-4 border-blue-500/20 flex items-center justify-center mx-auto mb-8 shadow-xl">
                   <span className="text-2xl font-black text-blue-400">{item.step}</span>
                 </div>
                 <h3 className="text-2xl font-bold">{item.title}</h3>
                 <p className="text-slate-400">{item.desc}</p>
               </div>
             ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-8 py-12 border-t border-white/5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <CloudLightning className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight">TallyGenius</span>
          </div>
          <div className="flex items-center gap-8 text-slate-500 text-sm">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Contact Support</a>
          </div>
          <p className="text-slate-600 text-sm">© 2026 TallyGenius Inc. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
