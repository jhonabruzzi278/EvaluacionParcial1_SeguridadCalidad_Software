// Migración al arrancar: las contraseñas guardadas en texto plano (bases creadas antes de la corrección de INC-02)
// se convierten a hash bcrypt. Es idempotente: no toca las filas que ya tienen hash.
const { pool } = require("./db");
const { hashPassword, esHashBcrypt } = require("./middleware/password");

async function migrarContrasenasLegadas() {
  const { rows } = await pool.query("SELECT id, contrasena_hash FROM usuarios");
  let migradas = 0;
  for (const u of rows) {
    if (esHashBcrypt(u.contrasena_hash)) continue;
    await pool.query("UPDATE usuarios SET contrasena_hash=$1 WHERE id=$2", [
      await hashPassword(u.contrasena_hash),
      u.id,
    ]);
    migradas++;
  }
  if (migradas > 0) console.log(`Migradas ${migradas} contraseña(s) a bcrypt`);
}

module.exports = { migrarContrasenasLegadas };
