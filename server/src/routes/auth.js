import { Router } from "express";
import bcrypt from "bcryptjs";
import { getPool } from "../lib/db.js";
import { signToken } from "../middleware/auth.js";

const router = Router();

router.post("/signup", async (req, res) => {
  const { email, password, name } = req.body || {};
  if (!email || !password || !name) {
    return res.status(400).json({ error: "email, password, and name are required" });
  }
  const passwordHash = await bcrypt.hash(password, 10);
  try {
    const pool = getPool();
    const [result] = await pool.query(
      "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
      [email, passwordHash, name]
    );
    const user = { id: result.insertId, email, name };
    const token = signToken(user);
    return res.status(201).json({ user, token });
  } catch (error) {
    if (error && error.code === "ER_DUP_ENTRY") {
      return res.status(409).json({ error: "Email already registered" });
    }
    return res.status(500).json({ error: "Signup failed" });
  }
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) {
    return res.status(400).json({ error: "email and password are required" });
  }
  try {
    const pool = getPool();
    const [rows] = await pool.query("SELECT * FROM users WHERE email = ?", [email]);
    const userRow = rows && rows[0];
    if (!userRow) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    const isValid = await bcrypt.compare(password, userRow.password_hash);
    if (!isValid) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    const user = { id: userRow.id, email: userRow.email, name: userRow.name };
    const token = signToken(user);
    return res.json({ user, token });
  } catch (_error) {
    return res.status(500).json({ error: "Login failed" });
  }
});

export default router;


