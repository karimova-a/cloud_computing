export const MODELS = {
    "gpt-4o-mini": { name: "GPT-4o-mini", inputRate: 0.15, outputRate: 0.60 },
    "claude-3-haiku": { name: "Claude 3 Haiku", inputRate: 0.25, outputRate: 1.25 },
    "gemini-1.5-flash": { name: "Gemini 1.5 Flash", inputRate: 0.075, outputRate: 0.30 },
    "custom": { name: "Custom", inputRate: 0.50, outputRate: 1.50 }
};

export const CONSTANTS = {
    SERVERLESS_INVOCATION_COST: 0.0000002, // cost per invocation
    DB_STORAGE_COST_PER_GB: 0.10, // cost per GB/month
    BANDWIDTH_COST_PER_GB: 0.05, // cost per GB
};

/**
 * Calculates the LLM inference cost.
 * Rates are per 1M tokens.
 */
export function calculateInferenceCost(mau, messagesPerUser, inputTokensPerMessage, outputTokensPerMessage, inputRatePer1M, outputRatePer1M) {
    const totalMessages = mau * messagesPerUser;
    const totalInputTokens = totalMessages * inputTokensPerMessage;
    const totalOutputTokens = totalMessages * outputTokensPerMessage;

    const inputCost = (totalInputTokens / 1_000_000) * inputRatePer1M;
    const outputCost = (totalOutputTokens / 1_000_000) * outputRatePer1M;

    return inputCost + outputCost;
}

/**
 * Calculates backend compute cost.
 */
export function calculateComputeCost(mau, messagesPerUser, costPerInvocation = CONSTANTS.SERVERLESS_INVOCATION_COST) {
    const totalInvocations = mau * messagesPerUser;
    return totalInvocations * costPerInvocation;
}

/**
 * Calculates storage cost.
 * storagePerMessage in KB.
 */
export function calculateStorageCost(mau, messagesPerUser, storagePerMessageKB, costPerGB = CONSTANTS.DB_STORAGE_COST_PER_GB) {
    const totalMessages = mau * messagesPerUser;
    const totalStorageKB = totalMessages * storagePerMessageKB;
    const totalStorageGB = totalStorageKB / 1_000_000; // Assuming 1 GB = 1,000,000 KB for simplicity, or 1024^2
    return totalStorageGB * costPerGB;
}

/**
 * Calculates bandwidth cost.
 * bandwidthPerMessage in KB.
 */
export function calculateBandwidthCost(mau, messagesPerUser, bandwidthPerMessageKB, costPerGB = CONSTANTS.BANDWIDTH_COST_PER_GB) {
    const totalMessages = mau * messagesPerUser;
    const totalBandwidthKB = totalMessages * bandwidthPerMessageKB;
    const totalBandwidthGB = totalBandwidthKB / 1_000_000;
    return totalBandwidthGB * costPerGB;
}

/**
 * Calculates the total cost incorporating all parameters.
 */
export function calculateTotalCost(inputs) {
    const {
        mau,
        messagesPerUser,
        inputTokens,
        outputTokens,
        modelId,
        storagePerMessageKB = 2,
        bandwidthPerMessageKB = 1
    } = inputs;

    const model = MODELS[modelId] || MODELS["custom"];

    const inference = calculateInferenceCost(mau, messagesPerUser, inputTokens, outputTokens, model.inputRate, model.outputRate);
    const compute = calculateComputeCost(mau, messagesPerUser);
    const storage = calculateStorageCost(mau, messagesPerUser, storagePerMessageKB);
    const bandwidth = calculateBandwidthCost(mau, messagesPerUser, bandwidthPerMessageKB);

    return {
        inference,
        compute,
        storage,
        bandwidth,
        total: inference + compute + storage + bandwidth
    };
}
