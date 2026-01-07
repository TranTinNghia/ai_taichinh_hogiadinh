import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from './components/ChatInterface';
import DashboardPage from './components/DashboardPage';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (prompt) => {
    setLoading(true);
    const userMessage = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await axios.post('/api/chat', { prompt });
      const aiMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = { role: 'assistant', content: 'Lỗi: ' + (error.response?.data?.error || error.message) };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (currentView === 'dashboard') {
    return (
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <div>
              <h1>Dashboard Metrics</h1>
              <p>Bảng đánh giá chi tiết các metrics</p>
            </div>
            <button className="nav-button" onClick={() => setCurrentView('chat')}>
              Quay lại Chat
            </button>
          </div>
        </header>
        <DashboardPage />
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>Đánh Giá Chatbot Gemini</h1>
            <p>Hệ thống đánh giá chất lượng câu trả lời AI</p>
          </div>
          <button className="nav-button" onClick={() => setCurrentView('dashboard')}>
            Xem Dashboard
          </button>
        </div>
      </header>
      <div className="app-content">
        <div className="app-main-full">
          <ChatInterface 
            messages={messages} 
            onSendMessage={handleSendMessage}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;

