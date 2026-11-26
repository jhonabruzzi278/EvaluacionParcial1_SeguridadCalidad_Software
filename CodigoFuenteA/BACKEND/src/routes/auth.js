const express = require("express");
const { pool } = require("../db");
const { signToken } = require("../middleware/auth");
const bcrypt = require("bcryptjs");
const { compararPassword, esHashBcrypt } = require("../middleware/password");

const router = express.Router();

// Función helper para simular latencia
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Hash ficticio para igualar el tiempo de respuesta cuando el usuario no existe (evita enumeración).
const HASH_FICTICIO = bcrypt.hashSync("hash-ficticio-sin-uso", 12);

// Login: usuario + contraseña verificada contra el hash bcrypt
router.post("/login", async (req, res) => {
  const { nombre_usuario, password } = req.body || {};
  try {
    // Simular latencia de 4 segundos
    await delay(4000);
    if (typeof nombre_usuario !== "string" || typeof password !== "string") {
      return res.status(400).json({ error: "Credenciales inválidas" });
    }
    const result = await pool.query(
      "SELECT id, nombre_usuario, contrasena_hash FROM usuarios WHERE nombre_usuario = $1",
      [nombre_usuario]
    );
    const user = result.rows[0];
    const hash = user && esHashBcrypt(user.contrasena_hash) ? user.contrasena_hash : HASH_FICTICIO;
    const coincide = await compararPassword(password, hash);
    if (!user || !coincide) {
      return res.status(401).json({ error: "Credenciales inválidas" });
    }

    // Vínculo más reciente del usuario con una empresa, y su rol
    const vinculo = await pool.query(
      `SELECT eu.id, eu.empresa_id, eu.rol_id, r.nombre AS rol
       FROM empresa_usuarios eu
       LEFT JOIN roles r ON r.id = eu.rol_id
       WHERE eu.usuario_id = $1
       ORDER BY eu.id DESC LIMIT 1`,
      [user.id]
    );
    const v = vinculo.rows[0] || {};

    const token = signToken({
      usuarioId: user.id,
      nombreUsuario: user.nombre_usuario,
      empresaUsuarioId: v.id || null,
      empresaId: v.empresa_id || null,
      rolId: v.rol_id || null,
      rol: v.rol || null,
    });

    // Registrar en auditoría
    await pool.query(
      "INSERT INTO auditoria (usuario_id, accion) VALUES ($1, $2)",
      [user.nombre_usuario, "LOGIN: usuario inició sesión"]
    );

    res.json({ token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error en login" });
  }
});

module.exports = router;
