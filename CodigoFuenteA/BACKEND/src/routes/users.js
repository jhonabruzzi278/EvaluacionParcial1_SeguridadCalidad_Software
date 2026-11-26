const express = require("express");
const { pool } = require("../db");
const { getUserFromAuthHeader } = require("../middleware/auth");
const { validarPolitica, hashPassword } = require("../middleware/password");

const router = express.Router();

// Crear usuario
router.post("/", async (req, res) => {
  const { nombre_usuario, contrasena_hash, correo } = req.body;
  try {
    const errorPolitica = validarPolitica(contrasena_hash);
    if (errorPolitica) {
      return res.status(400).json({ error: "Contraseña inválida", glosa: errorPolitica });
    }
    const result = await pool.query(
      "INSERT INTO usuarios (nombre_usuario, contrasena_hash, correo) VALUES ($1, $2, $3) RETURNING id, nombre_usuario, correo, created_at",
      [nombre_usuario, await hashPassword(contrasena_hash), correo]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({
      error: "Error al crear usuario",
      glosa: err.message || err.toString(),
    });
  }
});

// Listar usuarios filtrados por empresa del token
router.get("/", async (req, res) => {
  try {
    const authUser = getUserFromAuthHeader(req);
    console.log("authUser", authUser);
    /* console.log("authUser.empresaId", authUser.empresaId); */
    // Si no hay token o no hay empresaId, retornar error
    if (!authUser || !authUser.empresaId) {
      return res.status(401).json({
        error: "No autorizado",
        glosa: "Token inválido o sin empresa asociada",
      });
    }

    // Filtrar usuarios que pertenecen a la empresa del token
    const result = await pool.query(
      `SELECT DISTINCT u.id, u.nombre_usuario, u.correo, u.created_at 
       FROM usuarios u
       INNER JOIN empresa_usuarios eu ON eu.usuario_id = u.id
       WHERE eu.empresa_id = $1
       ORDER BY u.id DESC`,
      [authUser.empresaId]
    );

    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({
      error: "Error al listar usuarios",
      glosa: err.message || err.toString(),
    });
  }
});

// Obtener usuario por id
router.get("/:id", async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT u.id, u.nombre_usuario, u.correo, u.created_at FROM usuarios u
       WHERE u.id = $1 AND EXISTS (
         SELECT 1 FROM empresa_usuarios eu WHERE eu.usuario_id = u.id AND eu.empresa_id = $2)`,
      [req.params.id, req.user.empresaId]
    );
    if (result.rows.length === 0)
      return res.status(404).json({ error: "No encontrado" });
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({
      error: "Error al obtener usuario",
      glosa: err.message || err.toString(),
    });
  }
});

// Actualizar usuario
router.put("/:id", async (req, res) => {
  const { nombre_usuario, contrasena_hash, correo } = req.body;
  try {
    let nuevoHash = null;
    if (contrasena_hash !== undefined && contrasena_hash !== null && contrasena_hash !== "") {
      const errorPolitica = validarPolitica(contrasena_hash);
      if (errorPolitica) {
        return res.status(400).json({ error: "Contraseña inválida", glosa: errorPolitica });
      }
      nuevoHash = await hashPassword(contrasena_hash);
    }
    const result = await pool.query(
      `UPDATE usuarios SET nombre_usuario=$1, contrasena_hash=COALESCE($2, contrasena_hash), correo=$3
       WHERE id=$4 AND EXISTS (
         SELECT 1 FROM empresa_usuarios eu WHERE eu.usuario_id = usuarios.id AND eu.empresa_id = $5)
       RETURNING id, nombre_usuario, correo, created_at`,
      [nombre_usuario, nuevoHash, correo, req.params.id, req.user.empresaId]
    );
    if (result.rows.length === 0)
      return res.status(404).json({ error: "No encontrado" });

    const authUser = getUserFromAuthHeader(req);
    await pool.query(
      "INSERT INTO auditoria (usuario_id, accion) VALUES ($1, $2)",
      [
        authUser?.nombreUsuario || null,
        `USUARIOS_ACTUALIZAR: actualizó usuario ID ${req.params.id}`,
      ]
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({
      error: "Error al actualizar usuario",
      glosa: err.message || err.toString(),
    });
  }
});

// Eliminar usuario
router.delete("/:id", async (req, res) => {
  try {
    // Solo se elimina un usuario vinculado a la empresa del token (primero sus vínculos).
    const pertenece = await pool.query(
      "SELECT 1 FROM empresa_usuarios WHERE usuario_id=$1 AND empresa_id=$2",
      [req.params.id, req.user.empresaId]
    );
    if (pertenece.rows.length === 0)
      return res.status(404).json({ error: "No encontrado" });
    await pool.query("DELETE FROM empresa_usuarios WHERE usuario_id=$1", [req.params.id]);
    const result = await pool.query(
      "DELETE FROM usuarios WHERE id=$1 RETURNING id",
      [req.params.id]
    );
    if (result.rows.length === 0)
      return res.status(404).json({ error: "No encontrado" });

    const authUser = getUserFromAuthHeader(req);
    await pool.query(
      "INSERT INTO auditoria (usuario_id, accion) VALUES ($1, $2)",
      [
        authUser?.nombreUsuario || null,
        `USUARIOS_ELIMINAR: eliminó usuario ID ${req.params.id}`,
      ]
    );

    res.json({ deleted: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({
      error: "Error al eliminar usuario",
      glosa: err.message || err.toString(),
    });
  }
});

module.exports = router;
