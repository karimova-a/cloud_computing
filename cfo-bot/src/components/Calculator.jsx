import React from 'react';
import { MODELS } from '../utils/pricingModels';

export default function Calculator({ inputs, setInputs }) {
    const handleChange = (e) => {
        const { name, value, type } = e.target;
        setInputs(prev => ({
            ...prev,
            [name]: type === 'number' || type === 'range' ? Number(value) : value
        }));
    };

    return (
        <div className="glass-card">
            <h2>⚙️ Configuration</h2>

            <div className="input-group">
                <label>
                    <span>Monthly Active Users (MAU)</span>
                    <span>{inputs.mau.toLocaleString()}</span>
                </label>
                <input
                    type="range"
                    name="mau"
                    min="100"
                    max="100000"
                    step="100"
                    value={inputs.mau}
                    onChange={handleChange}
                />
            </div>

            <div className="input-group">
                <label>
                    <span>Messages per User / Month</span>
                    <span>{inputs.messagesPerUser}</span>
                </label>
                <input
                    type="range"
                    name="messagesPerUser"
                    min="1"
                    max="500"
                    value={inputs.messagesPerUser}
                    onChange={handleChange}
                />
            </div>

            <div className="input-group">
                <label>
                    <span>Average Input Tokens / Msg</span>
                    <span>{inputs.inputTokens}</span>
                </label>
                <input
                    type="range"
                    name="inputTokens"
                    min="10"
                    max="2000"
                    value={inputs.inputTokens}
                    onChange={handleChange}
                />
            </div>

            <div className="input-group">
                <label>
                    <span>Average Output Tokens / Msg</span>
                    <span>{inputs.outputTokens}</span>
                </label>
                <input
                    type="range"
                    name="outputTokens"
                    min="10"
                    max="2000"
                    value={inputs.outputTokens}
                    onChange={handleChange}
                />
            </div>

            <div className="input-group">
                <label>AI Model Selection</label>
                <select name="modelId" value={inputs.modelId} onChange={handleChange}>
                    {Object.entries(MODELS).map(([id, model]) => (
                        <option key={id} value={id}>
                            {model.name} (${model.inputRate} In / ${model.outputRate} Out)
                        </option>
                    ))}
                </select>
            </div>

        </div>
    );
}
