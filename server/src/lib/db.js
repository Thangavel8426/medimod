import mysql from "mysql2/promise";

let pool;

export function getPool() {
  if (!pool) {
    throw new Error("Database pool not initialized. Call initDatabase() first.");
  }
  return pool;
}

export async function initDatabase() {
  const host = process.env.DB_HOST || "localhost";
  const user = process.env.DB_USER || "root";
  const password = process.env.DB_PASSWORD || "";
  const database = process.env.DB_NAME || "meditrack";

  pool = mysql.createPool({
    host,
    user,
    password,
    database,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
  });

  await ensureSchema();
}

async function ensureSchema() {
  const connection = await pool.getConnection();
  try {
    await connection.query(
      `CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      ) ENGINE=InnoDB;`
    );

    await connection.query(
      `CREATE TABLE IF NOT EXISTS reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        week_start DATE NOT NULL,
        blood_sugar FLOAT NULL,
        systolic_bp INT NULL,
        diastolic_bp INT NULL,
        jaundice_index FLOAT NULL,
        analysis JSON NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE KEY unique_user_week (user_id, week_start)
      ) ENGINE=InnoDB;`
    );

    await connection.query(
      `CREATE TABLE IF NOT EXISTS health_analyses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        report_type VARCHAR(50) NOT NULL,
        parameters JSON NOT NULL,
        analysis_result JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_analysis_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      ) ENGINE=InnoDB;`
    );
  } finally {
    connection.release();
  }
}


