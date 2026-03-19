import React from 'react';
import { calculateTotalCost } from '../utils/pricingModels';

export default function ResultsDashboard({ inputs }) {
    const costs = calculateTotalCost(inputs);

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    };

    return (
        <div className="glass-card">
            <h2>📊 Cost Breakdown</h2>

            <div className="result-item">
                <span className="result-label">🧠 LLM Inference Cost</span>
                <span className="result-value">{formatCurrency(costs.inference)}</span>
            </div>

            <div className="result-item">
                <span className="result-label">⚡ Backend Compute Cost</span>
                <span className="result-value">{formatCurrency(costs.compute)}</span>
            </div>

            <div className="result-item">
                <span className="result-label">🗄️ Database Storage Cost</span>
                <span className="result-value">{formatCurrency(costs.storage)}</span>
            </div>

            <div className="result-item">
                <span className="result-label">🌐 Network Bandwidth Cost</span>
                <span className="result-value">{formatCurrency(costs.bandwidth)}</span>
            </div>

            <div className="total-cost">
                <p>Estimated Monthly Cost</p>
                <h3>{formatCurrency(costs.total)}</h3>
            </div>
        </div>
    );
}
