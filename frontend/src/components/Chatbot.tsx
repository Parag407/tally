import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { MessageSquare, X, Send, Bot, User, Loader2, Sparkles } from 'lucide-react';

interface ChatbotProps {
  errors: any[];
  fileName?: string;
  onActionTriggered?: (action: string) => void;
}

interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
}

const Chatbot: React.FC<ChatbotProps> = ({ errors, fileName, onActionTriggered }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([{
    role: 'bot',
    content: "Hi! I'm your AI assistant. Do you need help fixing Excel errors or generating your XML?"
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen, loading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/api/chat/`, {
        message: userMessage,
        errors: errors || [],
        fileName: fileName || "None uploaded"
      });

      let reply = response.data.response;
      
      // Parse for action triggers
      const actionMatch = reply.match(/\[ACTION:([A-Z_]+)\]/);
      if (actionMatch) {
        const action = actionMatch[1];
        if (onActionTriggered) {
          onActionTriggered(action);
        }
        // Remove the action code from the visible reply
        reply = reply.replace(/\[ACTION:[A-Z_]+\]/g, '').trim();
      }

      setMessages(prev => [...prev, { role: 'bot', content: reply }]);
    } catch (error: any) {
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: error.response?.data?.detail || "Sorry, I'm having trouble connecting. Make sure your OpenAI API key is valid!" 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {isOpen ? (
        <div className="bg-[#0f172a] rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/10 w-80 sm:w-96 flex flex-col overflow-hidden mb-4 transition-all duration-300 transform origin-bottom-right backdrop-blur-2xl animate-fade-in">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-5 flex justify-between items-center text-white shadow-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white/20">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm tracking-tight">Smart Guide AI</h3>
                <p className="text-[10px] text-blue-100 font-bold uppercase tracking-wider">Online Assistant</p>
              </div>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-white/80 hover:text-white transition-colors p-2 rounded-xl hover:bg-white/10"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Body */}
          <div className="flex-1 min-h-[300px] max-h-[450px] overflow-y-auto p-5 space-y-4 custom-scrollbar">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`shrink-0 w-8 h-8 rounded-xl flex items-center justify-center shadow-lg ${msg.role === 'user' ? 'bg-blue-600' : 'bg-[#020617] border border-white/10'}`}>
                    {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-blue-400" />}
                  </div>
                  <div className={`p-3.5 rounded-2xl text-[13px] leading-relaxed font-medium ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none' 
                      : 'bg-white/5 border border-white/10 text-slate-300 rounded-tl-none'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-3 max-w-[85%] flex-row text-slate-500 font-bold">
                  <div className="shrink-0 w-8 h-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="p-3.5 bg-white/5 border border-white/10 rounded-2xl rounded-tl-none flex items-center gap-2 shadow-sm text-xs italic">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-500" /> AI Analyzing...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Footer / Input */}
          <div className="p-4 bg-[#020617] border-t border-white/5">
            <div className="relative flex items-center gap-2">
              <input 
                type="text" 
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Ask GPT for help..."
                className="w-full bg-white/5 text-sm py-3 pl-4 pr-12 rounded-xl border border-white/10 text-white focus:bg-white/10 focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-600"
                disabled={loading}
              />
              <button 
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="absolute right-1.5 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 transition-all active:scale-90"
                title="Send"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <button 
          onClick={() => setIsOpen(true)}
          className="w-16 h-16 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl shadow-[0_10px_30px_rgba(59,130,246,0.5)] hover:shadow-[0_15px_40px_rgba(59,130,246,0.6)] hover:scale-110 active:scale-95 transition-all duration-300 flex items-center justify-center group relative overflow-hidden"
        >
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <MessageSquare className="w-8 h-8 relative z-10 drop-shadow-lg" />
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-[#0f172a] animate-pulse"></div>
        </button>
      )}
    </div>
  );
};

export default Chatbot;
