import { Router } from "express";
import { spawn } from "child_process";

const router = Router();

router.post("/", (req, res) => {
    const { expression, variable } = req.body;
    const pythonProcess = spawn("python3", ["./scripts/integration.py", expression.toString(), variable]);
    let result: string = "";
    let errorOccurred = false;

    pythonProcess.stdout.on("data", (data: Buffer) => {
        result += data.toString();
    });

    pythonProcess.stdout.on("close", (code: number) => {
        if (!errorOccurred) {
            res.json({ result });
            console.log("Process closed with code: ", code);
        }
    });

    pythonProcess.stderr.on("data", (data: Buffer) => {
        errorOccurred = true;
        console.log("Error: ", data.toString());
        res.status(500).send(data.toString());
    });
});

export default router;