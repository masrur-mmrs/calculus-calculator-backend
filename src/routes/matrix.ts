import { Router, Request, Response } from "express";
import { pythonMatrixService } from "../services/python-matrix-service";

const router = Router();

router.post("/", async (req: Request, res: Response): Promise<void> => {
  try {
    const { expression } = req.body;
    
    if (!expression) {
        res.status(400).json({ error: "Missing required parameter: expression" });
        return;
    }
    
    const result = await pythonMatrixService.evaluateMatrix(expression);
    res.json({ result });
  } catch (error) {
    console.error("Matrix operation error:", error);
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;