import dotenv from "dotenv";
dotenv.config();

import { createServer } from "http";
import app from "./app.js";
import { initDatabase } from "./lib/db.js";

const port = process.env.PORT || 4000;

async function start() {
  await initDatabase();
  const httpServer = createServer(app);
  httpServer.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`MediTrack server running on http://localhost:${port}`);
  });
}

start().catch((error) => {
  // eslint-disable-next-line no-console
  console.error("Failed to start server:", error);
  process.exit(1);
});


