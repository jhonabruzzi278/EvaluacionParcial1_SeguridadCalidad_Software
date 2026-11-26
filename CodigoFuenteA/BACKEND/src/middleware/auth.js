// Autenticación y autorización centralizadas (corrige INC-01, INC-03 e INC-04).
//  - El secreto JWT es obligatorio, robusto y nunca tiene un valor por defecto (OWASP A07, NFR-SEG-9).
//  - Solo se aceptan tokens HS256 (rechaza alg=none) con expiración.
//  - Las escrituras exigen rol administrador en el backend (RB-4, NFR-SEG-4, OWASP A01).
const jwt = require("jsonwebtoken");

const SECRETOS_PROHIBIDOS = new Set([
  "inseguro",
  "your-secret-key-change-in-production",
  "secret",
  "changeme",
]);

const JWT_SECRET = process.env.JWT_SECRET || "";
if (JWT_SECRET.length < 32 || SECRETOS_PROHIBIDOS.has(JWT_SECRET)) {
  throw new Error(
    "JWT_SECRET no definido o inseguro: debe tener al menos 32 caracteres (ej. openssl rand -hex 32)"
  );
}

const ROL_ADMIN = "administrador";

function signToken(payload) {
  return jwt.sign(payload, JWT_SECRET, { algorithm: "HS256", expiresIn: "2h" });
}

function verifyBearer(req) {
  const auth = req.headers.authorization || "";
  if (!auth.startsWith("Bearer ")) return null;
  try {
    return jwt.verify(auth.substring(7), JWT_SECRET, { algorithms: ["HS256"] });
  } catch {
    return null;
  }
}

// Usuario autenticado: el que dejó `authenticate` o, en rutas públicas, el del token si viene uno.
function getUserFromAuthHeader(req) {
  return req.user || verifyBearer(req);
}

function authenticate(req, res, next) {
  const user = verifyBearer(req);
  if (!user || !user.empresaId) {
    return res.status(401).json({
      error: "No autorizado",
      glosa: "Token inválido o sin empresa asociada",
    });
  }
  req.user = user;
  next();
}

// Lectura para cualquier rol; escritura solo para administradores.
function requireAdminForWrites(req, res, next) {
  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) return next();
  if (req.user && req.user.rol === ROL_ADMIN) return next();
  return res.status(403).json({
    error: "Prohibido",
    glosa: "Se requiere rol administrador para esta operación",
  });
}

// Aplica los middlewares salvo a las rutas públicas indicadas (p. ej. el registro con POST).
function exceptMethods(methods, ...middlewares) {
  return (req, res, next) => {
    if (methods.includes(req.method)) return next();
    let i = 0;
    const run = (err) => {
      if (err || i >= middlewares.length) return next(err);
      middlewares[i++](req, res, run);
    };
    run();
  };
}

module.exports = {
  ROL_ADMIN,
  signToken,
  authenticate,
  requireAdminForWrites,
  exceptMethods,
  getUserFromAuthHeader,
};
