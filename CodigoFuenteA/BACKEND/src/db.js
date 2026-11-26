const { Pool } = require("pg");
require("dotenv").config();

// La conexión se configura solo por entorno: no hay credenciales por defecto en el código.
if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL no está definida");
}

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

module.exports = { pool };
