import { Router } from "express";
import axios from "axios";
import { getPool } from "../lib/db.js";
import { requireAuth } from "../middleware/auth.js";

const router = Router();

// Public endpoint for analysis (no auth required for demo)
router.post("/analyze", async (req, res) => {
  const mlUrl = process.env.ML_SERVICE_URL || "http://localhost:8000";
  try {
    const { data } = await axios.post(`${mlUrl}/analyze`, req.body, { timeout: 10000 });
    
    // Store analysis in database if user is authenticated
    if (req.user) {
      try {
        const pool = getPool();
        await pool.query(
          `INSERT INTO health_analyses (user_id, report_type, parameters, analysis_result, created_at) 
           VALUES (?, ?, ?, ?, NOW())`,
          [
            req.user.id,
            data.report_type,
            JSON.stringify(req.body.parameters),
            JSON.stringify(data)
          ]
        );
      } catch (dbError) {
        console.error("Failed to store analysis:", dbError);
        // Don't fail the request if DB storage fails
      }
    }
    
    return res.json(data);
  } catch (error) {
    console.error("Analysis error:", error);
    const message = error?.response?.data || error?.message || "ML service error";
    return res.status(502).json({ error: message });
  }
});

// Get analysis history for authenticated users
router.get("/history", requireAuth, async (req, res) => {
  try {
    const pool = getPool();
    const [rows] = await pool.query(
      `SELECT * FROM health_analyses 
       WHERE user_id = ? 
       ORDER BY created_at DESC 
       LIMIT 20`,
      [req.user.id]
    );
    
    return res.json(rows);
  } catch (error) {
    console.error("History fetch error:", error);
    return res.status(500).json({ error: "Failed to fetch analysis history" });
  }
});

// Get health standards
router.get("/standards", async (req, res) => {
  const mlUrl = process.env.ML_SERVICE_URL || "http://localhost:8000";
  try {
    const { data } = await axios.get(`${mlUrl}/standards`, { timeout: 5000 });
    return res.json(data);
  } catch (error) {
    console.error("Standards fetch error:", error);
    return res.status(502).json({ error: "Failed to fetch health standards" });
  }
});

export default router;


