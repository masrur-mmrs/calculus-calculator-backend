import { Router, Request, Response } from "express";
import { pythonDerivativeStepsService } from "../services/python-derivative-steps-service";

const router = Router();

router.post("/", async (req: Request, res: Response): Promise<void> => {
  try {
    const { expression, variable, orderOfDerivative } = req.body;

    if (!expression || !variable || !orderOfDerivative) {
        res.status(400).json({ error: "Missing required parameters" });
        return;
    }

    const rawResponse = await pythonDerivativeStepsService.differentiate_with_steps(expression, variable, orderOfDerivative);
    const responsePayload = typeof rawResponse === "string" ? JSON.parse(rawResponse) : rawResponse;
    res.json(responsePayload);
  } catch (error) {
    console.error("Error generating derivative steps:", error);
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;