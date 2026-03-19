import { describe, it, expect } from 'vitest';
import {
    calculateInferenceCost,
    calculateComputeCost,
    calculateStorageCost,
    calculateBandwidthCost,
    calculateTotalCost
} from '../utils/pricingModels';

describe('Pricing Models Math Operations', () => {

    it('1. LLM Inference Cost Tests', () => {
        // 1,000 MAU, 50 msg/user, 100 in/msg, 200 out/msg. Model: $0.50/1M in, $1.50/1M out.
        const cost = calculateInferenceCost(1000, 50, 100, 200, 0.50, 1.50);
        // 5,000,000 input tokens -> $2.50
        // 10,000,000 output tokens -> $15.00
        // Total: 17.50
        expect(cost).toBeCloseTo(17.50, 4);
    });

    it('2. Backend Compute Cost Tests', () => {
        // 1000 MAU, 50 msg/user, $0.0000002 cost.
        const cost = calculateComputeCost(1000, 50, 0.0000002);
        // 50,000 invocations * 0.0000002 = 0.01
        expect(cost).toBeCloseTo(0.01, 4);
    });

    it('3. Storage Cost Tests', () => {
        // 1000 MAU, 50 msg/user, 2KB/msg, $0.10/GB
        const cost = calculateStorageCost(1000, 50, 2, 0.10);
        // 100,000 KB = 0.1 GB
        // 0.1 GB * 0.10 = 0.01
        expect(cost).toBeCloseTo(0.01, 4);
    });

    it('4. Bandwidth Cost Tests', () => {
        // 1000 MAU, 50 msg/user, 1KB/msg, $0.05/GB
        const cost = calculateBandwidthCost(1000, 50, 1, 0.05);
        // 50,000 KB = 0.05 GB
        // 0.05 GB * 0.05 = 0.0025
        expect(cost).toBeCloseTo(0.0025, 4);
    });

    it('5. Total Cost Integration Test', () => {
        const inputs = {
            mau: 1000,
            messagesPerUser: 50,
            inputTokens: 100,
            outputTokens: 200,
            modelId: 'custom',
            storagePerMessageKB: 2,
            bandwidthPerMessageKB: 1
        };
        // The "custom" model is defined as 0.50 in, 1.50 out in MODELS, exactly matching our tests.
        const result = calculateTotalCost(inputs);
        // 17.50 + 0.01 + 0.01 + 0.0025 = 17.5225
        expect(result.total).toBeCloseTo(17.5225, 4);
        expect(result.inference).toBeCloseTo(17.50, 4);
        expect(result.compute).toBeCloseTo(0.01, 4);
        expect(result.storage).toBeCloseTo(0.01, 4);
        expect(result.bandwidth).toBeCloseTo(0.0025, 4);
    });

});
