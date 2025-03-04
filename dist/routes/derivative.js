"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const child_process_1 = require("child_process");
const router = (0, express_1.Router)();
router.post("/derivative", (req, res) => {
    console.log("Request received: ", req.body);
    const { expression, variable } = req.body;
    const pythonProcess = (0, child_process_1.spawn)("python3", ["../../scripts/differentiation.py", expression, variable]);
    let result = "";
    pythonProcess.stdout.on("data", (data) => {
        // res.send(data.toString());
        result += data.toString();
    });
    pythonProcess.stdout.on("close", (code) => {
        res.json({ result });
        console.log("Process closed with code: ", code);
    });
    pythonProcess.stderr.on("data", (data) => {
        console.log("Error: ", data);
        res.send(data.toString());
    });
});
exports.default = router;
