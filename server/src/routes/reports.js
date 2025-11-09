import { Router } from "express";
import { getPool } from "../lib/db.js";
import { requireAuth } from "../middleware/auth.js";

const router = Router();

router.use(requireAuth);

// Create or update a weekly report
router.post("/", async (req, res) => {
  const userId = req.user.id;
  const {
    weekStart,
    bloodSugar,
    systolicBp,
    diastolicBp,
    jaundiceIndex,
    analysis,
  } = req.body || {};

  if (!weekStart) {
    return res.status(400).json({ error: "weekStart (YYYY-MM-DD) is required" });
  }

  try {
    const pool = getPool();
    const [result] = await pool.query(
      `INSERT INTO reports (user_id, week_start, blood_sugar, systolic_bp, diastolic_bp, jaundice_index, analysis)
       VALUES (?, ?, ?, ?, ?, ?, CAST(? AS JSON))
       ON DUPLICATE KEY UPDATE blood_sugar = VALUES(blood_sugar), systolic_bp = VALUES(systolic_bp), diastolic_bp = VALUES(diastolic_bp), jaundice_index = VALUES(jaundice_index), analysis = VALUES(analysis)`,
      [
        userId,
        weekStart,
        bloodSugar ?? null,
        systolicBp ?? null,
        diastolicBp ?? null,
        jaundiceIndex ?? null,
        analysis ? JSON.stringify(analysis) : null,
      ]
    );
    return res.status(result.affectedRows ? 200 : 201).json({ ok: true });
  } catch (error) {
    return res.status(500).json({ error: "Failed to save report" });
  }
});

// Get recent reports for user
router.get("/", async (req, res) => {
  const userId = req.user.id;
  try {
    const pool = getPool();
    const [rows] = await pool.query(
      "SELECT * FROM reports WHERE user_id = ? ORDER BY week_start DESC LIMIT 12",
      [userId]
    );
    return res.json(rows);
  } catch (_error) {
    return res.status(500).json({ error: "Failed to fetch reports" });
  }
});

export default router;


