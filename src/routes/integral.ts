import { Router, Request, Response } from "express";
import { pythonIntegrationService } from "../services/python-integration-service";

const router = Router();

router.post("/", async (req: Request, res: Response): Promise<void> => {
  try {
    const { expression, variable } = req.body;
    
    if (!expression || !variable) {
      res.status(400).json({ error: "Missing required parameters" });
    }
    
    const result = await pythonIntegrationService.integrate(expression, variable);
    res.json({ result });
  } catch (error) {
    console.error("Integration error:", error);
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;