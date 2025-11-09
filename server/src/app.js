import express from "express";
import cors from "cors";

import authRouter from "./routes/auth.js";
import reportsRouter from "./routes/reports.js";
import analysisRouter from "./routes/analysis.js";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.use("/api/auth", authRouter);
app.use("/api/reports", reportsRouter);
app.use("/api/analysis", analysisRouter);

export default app;


