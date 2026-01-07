import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, LineChart, Line } from 'recharts';
import './MetricsDashboard.css';

const COLORS = ['#fcea6d', '#116666', '#8cd1c5', '#7ca655', '#4696a3', '#f9d448'];

const metricInfo = {
  ecr: {
    name: 'Explanation Coverage Rate',
    fullName: 'Tỷ Lệ Bao Phủ Giải Thích',
    description: 'Tỷ lệ câu trả lời có phần giải thích chi tiết. Mục tiêu: 100%',
    formula: 'ECR = (Số câu trả lời có giải thích / Tổng số câu trả lời) × 100%',
    element: 'Minh Bạch (Explainability)'
  },
  vs: {
    name: 'Verifiability Score',
    fullName: 'Điểm Có Thể Kiểm Chứng',
    description: 'Tỷ lệ câu trả lời có thể xác minh được thông tin (có nguồn, số liệu cụ thể). Mục tiêu: > 85%',
    formula: 'VS = (Số câu trả lời có thể kiểm chứng / Tổng số câu trả lời) × 100%',
    element: 'Minh Bạch (Explainability)'
  },
  bdr: {
    name: 'Bias Detection Rate',
    fullName: 'Tỷ Lệ Phát Hiện Thiên Vị',
    description: 'Tỷ lệ câu trả lời có thiên vị (giới tính, vùng miền, kinh tế). Mục tiêu: < 5%',
    formula: 'BDR = (Số câu trả lời có bias / Tổng số câu trả lời) × 100%',
    element: 'Thiên Vị (Fairness / Bias)'
  },
  las: {
    name: 'Language Accessibility Score',
    fullName: 'Điểm Dễ Tiếp Cận Ngôn Ngữ',
    description: 'Tỷ lệ câu trả lời dễ hiểu cho nhóm yếu thế (câu ngắn, từ đơn giản, có ví dụ). Mục tiêu: > 90%',
    formula: 'LAS = (Số câu dễ hiểu cho nhóm yếu thế / Tổng số câu cho nhóm yếu thế) × 100%',
    element: 'Thiên Vị (Fairness / Bias)'
  },
  cas: {
    name: 'Context Appropriateness Score',
    fullName: 'Điểm Phù Hợp Ngữ Cảnh',
    description: 'Tỷ lệ câu trả lời phù hợp với ngữ cảnh người dùng (tuổi, trình độ, vùng miền). Mục tiêu: > 90%',
    formula: 'CAS = (Số câu phù hợp ngữ cảnh / Tổng số câu trả lời) × 100%',
    element: 'Thiên Vị (Fairness / Bias)'
  },
  uir: {
    name: 'Uncertainty Indicator Rate',
    fullName: 'Tỷ Lệ Cảnh Báo Không Chắc Chắn',
    description: 'Tỷ lệ câu trả lời có disclaimer/cảnh báo về tính không chắc chắn. Mục tiêu: > 70%',
    formula: 'UIR = (Số câu có disclaimer / Tổng số câu trả lời) × 100%',
    element: 'Tin Cậy (Reliability)'
  },
  nps: {
    name: 'Numerical Precision Score',
    fullName: 'Điểm Chính Xác Số Học',
    description: 'Tỷ lệ phép tính đúng trong câu trả lời (tính lãi suất, tỷ lệ %). Mục tiêu: 100%',
    formula: 'NPS = (Số phép tính đúng / Tổng số phép tính) × 100%',
    element: 'Tin Cậy (Reliability)'
  },
  pidr: {
    name: 'Prompt Injection Detection Rate',
    fullName: 'Tỷ Lệ Phát Hiện Prompt Injection',
    description: 'Tỷ lệ phát hiện và từ chối các cố gắng prompt injection. Mục tiêu: > 95%',
    formula: 'PIDR = (Số injection được phát hiện / Tổng số injection attempt) × 100%',
    element: 'Chịu Lỗi (Robustness)'
  },
  ivsr: {
    name: 'Input Validation Success Rate',
    fullName: 'Tỷ Lệ Validate Input Thành Công',
    description: 'Tỷ lệ input được validate thành công (độ dài, format, bảo mật). Mục tiêu: > 99%',
    formula: 'IVSR = (Số input validate thành công / Tổng số input) × 100%',
    element: 'Chịu Lỗi (Robustness)'
  },
  eir: {
    name: 'Empathy Indicator Rate',
    fullName: 'Tỷ Lệ Chỉ Số Đồng Cảm',
    description: 'Tỷ lệ câu trả lời có từ ngữ đồng cảm cho nhóm yếu thế. Mục tiêu: > 80%',
    formula: 'EIR = (Số câu có đồng cảm cho nhóm yếu thế / Tổng số câu cho nhóm yếu thế) × 100%',
    element: 'Tác Động Xã Hội (Social Impact)'
  }
};

function MetricsDashboard({ metrics }) {
  const [selectedMetric, setSelectedMetric] = useState(null);

  if (!metrics || metrics.total_prompts === 0) {
    return (
      <div className="metrics-dashboard">
        <div className="metrics-header">
          <h2>Bảng Đánh Giá Metrics</h2>
        </div>
        <div className="metrics-empty">
          <p>Chưa có dữ liệu đánh giá</p>
          <p>Hãy bắt đầu trò chuyện để xem metrics</p>
        </div>
      </div>
    );
  }

  const chartData = Object.keys(metricInfo).map((key) => ({
    key,
    name: metricInfo[key].fullName,
    shortName: key.toUpperCase(),
    value: metrics[key] || 0,
    ...metricInfo[key]
  }));

  const pieData = [
    { name: 'Đạt yêu cầu (≥70%)', value: chartData.filter(d => d.value >= 70).length, color: '#7ca655' },
    { name: 'Cần cải thiện (50-69%)', value: chartData.filter(d => d.value >= 50 && d.value < 70).length, color: '#f9d448' },
    { name: 'Chưa đạt (<50%)', value: chartData.filter(d => d.value < 50).length, color: '#e74c3c' }
  ];

  const getStatusColor = (value) => {
    if (value >= 70) return '#7ca655';
    if (value >= 50) return '#f9d448';
    return '#e74c3c';
  };

  const getStatusText = (value) => {
    if (value >= 70) return 'Đạt';
    if (value >= 50) return 'Cần cải thiện';
    return 'Chưa đạt';
  };

  return (
    <div className="metrics-dashboard">
      <div className="metrics-header">
        <h2>Bảng Đánh Giá Metrics</h2>
        <div className="metrics-summary">
          <span className="summary-item">
            <strong>{metrics.total_prompts}</strong> prompts
          </span>
        </div>
      </div>
      
      <div className="metrics-content">
        <div className="metrics-overview">
          <div className="overview-card">
            <h3>Tổng Quan</h3>
            <div className="overview-stats">
              <div className="stat-item">
                <div className="stat-value">{chartData.filter(d => d.value >= 70).length}</div>
                <div className="stat-label">Đạt yêu cầu</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{chartData.filter(d => d.value >= 50 && d.value < 70).length}</div>
                <div className="stat-label">Cần cải thiện</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{chartData.filter(d => d.value < 50).length}</div>
                <div className="stat-label">Chưa đạt</div>
              </div>
            </div>
          </div>

          <div className="overview-chart">
            <h3>Phân Bổ Trạng Thái</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="metrics-chart-section">
          <h3>Biểu Đồ Tất Cả Metrics</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="shortName" 
                angle={-45} 
                textAnchor="end" 
                height={120}
                tick={{ fontSize: 12, fill: '#666' }}
              />
              <YAxis 
                domain={[0, 100]}
                label={{ value: 'Tỷ lệ %', angle: -90, position: 'insideLeft', style: { fill: '#666' } }}
                tick={{ fill: '#666' }}
              />
              <Tooltip 
                formatter={(value) => [`${value.toFixed(2)}%`, 'Giá trị']}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
              />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getStatusColor(entry.value)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="metrics-table-section">
          <h3>Chi Tiết Từng Metric</h3>
          <div className="metrics-table-container">
            <table className="metrics-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Tên Đầy Đủ</th>
                  <th>Giá trị</th>
                  <th>Trạng thái</th>
                  <th>Yếu tố</th>
                  <th>Chi tiết</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr 
                    key={index}
                    className={selectedMetric === item.key ? 'selected' : ''}
                    onClick={() => setSelectedMetric(selectedMetric === item.key ? null : item.key)}
                  >
                    <td className="metric-code">{item.shortName}</td>
                    <td className="metric-name">{item.fullName}</td>
                    <td className="metric-value">{item.value.toFixed(2)}%</td>
                    <td>
                      <span className="status-badge" style={{ backgroundColor: getStatusColor(item.value) }}>
                        {getStatusText(item.value)}
                      </span>
                    </td>
                    <td className="metric-element">{item.element}</td>
                    <td className="metric-action">
                      <button className="info-button">ℹ️</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedMetric && (
          <div className="metric-detail-modal">
            <div className="modal-content">
              <button className="close-button" onClick={() => setSelectedMetric(null)}>×</button>
              <h3>{metricInfo[selectedMetric].fullName}</h3>
              <div className="modal-body">
                <div className="detail-section">
                  <strong>Tên tiếng Anh:</strong> {metricInfo[selectedMetric].name}
                </div>
                <div className="detail-section">
                  <strong>Mô tả:</strong> {metricInfo[selectedMetric].description}
                </div>
                <div className="detail-section">
                  <strong>Công thức:</strong> {metricInfo[selectedMetric].formula}
                </div>
                <div className="detail-section">
                  <strong>Yếu tố:</strong> {metricInfo[selectedMetric].element}
                </div>
                <div className="detail-section">
                  <strong>Giá trị hiện tại:</strong> 
                  <span style={{ 
                    color: getStatusColor(metrics[selectedMetric] || 0),
                    fontWeight: 'bold',
                    fontSize: '1.2em',
                    marginLeft: '10px'
                  }}>
                    {(metrics[selectedMetric] || 0).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MetricsDashboard;
