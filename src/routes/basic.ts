import { Router, Request, Response } from "express";
import { pythonBasicService } from "../services/python-basic-service";

const router = Router();

router.post("/", async (req: Request, res: Response): Promise<void> => {
  try {
    const { expression } = req.body;

    if (!expression) {
      res.status(400).json({ error: "Missing required parameters" });
      return;
    }

    const result = await pythonBasicService.evaluateExpression(expression);
    res.json({ result });
  } catch (error) {
    console.error("Basic evaluation error:", error);
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;