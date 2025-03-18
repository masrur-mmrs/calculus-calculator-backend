"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const python_differentiation_service_1 = require("../services/python-differentiation-service");
const router = (0, express_1.Router)();
router.post("/", async (req, res) => {
    try {
        const { expression, variable } = req.body;
        if (!expression || !variable) {
            res.status(400).json({ error: "Missing required parameters" });
        }
        const result = await python_differentiation_service_1.pythonDifferentiationService.differentiate(expression, variable);
        res.json({ result });
    }
    catch (error) {
        console.error("Differentiation error:", error);
        res.status(500).json({ error: error.message });
    }
});
exports.default = router;
