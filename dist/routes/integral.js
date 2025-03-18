"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const python_integration_service_1 = require("../services/python-integration-service");
const router = (0, express_1.Router)();
router.post("/", async (req, res) => {
    try {
        const { expression, variable } = req.body;
        if (!expression || !variable) {
            res.status(400).json({ error: "Missing required parameters" });
        }
        const result = await python_integration_service_1.pythonIntegrationService.integrate(expression, variable);
        res.json({ result });
    }
    catch (error) {
        console.error("Integration error:", error);
        res.status(500).json({ error: error.message });
    }
});
exports.default = router;
