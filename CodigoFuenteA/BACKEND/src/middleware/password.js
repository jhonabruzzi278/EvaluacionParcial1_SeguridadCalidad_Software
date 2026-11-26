// Política y hashing de contraseñas (corrige INC-02 · NFR-SEG-2, Ley 19.628 art. 11).
const bcrypt = require("bcryptjs");

const COSTO = 12;

// ≥ 12 caracteres, mayúscula, minúscula, número y símbolo.
function validarPolitica(password) {
  if (typeof password !== "string") return "La contraseña es obligatoria";
  if (password.length < 12) return "La contraseña debe tener al menos 12 caracteres";
  if (!/[a-z]/.test(password)) return "La contraseña debe incluir una minúscula";
  if (!/[A-Z]/.test(password)) return "La contraseña debe incluir una mayúscula";
  if (!/[0-9]/.test(password)) return "La contraseña debe incluir un número";
  if (!/[^A-Za-z0-9]/.test(password)) return "La contraseña debe incluir un símbolo";
  return null;
}

const hashPassword = (password) => bcrypt.hash(password, COSTO);
const compararPassword = (password, hash) => bcrypt.compare(password, hash);
const esHashBcrypt = (valor) => /^\$2[aby]\$/.test(valor || "");

module.exports = { validarPolitica, hashPassword, compararPassword, esHashBcrypt };
