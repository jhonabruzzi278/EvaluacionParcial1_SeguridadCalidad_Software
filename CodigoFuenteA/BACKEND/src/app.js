const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const swaggerUi = require("swagger-ui-express");

const { pool } = require("./db");
const {
  authenticate,
  requireAdminForWrites,
  exceptMethods,
} = require("./middleware/auth");
const { migrarContrasenasLegadas } = require("./migraciones");

const authRoutes = require("./routes/auth");
const userRoutes = require("./routes/users");
const clientRoutes = require("./routes/clients");
const contractRoutes = require("./routes/contracts");
const auditRoutes = require("./routes/audit");
const empresasRoutes = require("./routes/empresas");
const rolesRoutes = require("./routes/roles");
const empresaUsuariosRoutes = require("./routes/empresa_usuarios");
const metricasRoutes = require("./routes/metricas");

const app = express();

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

// El registro (POST /usuarios y POST /empresas) y el login son públicos; el resto exige token.
// Las escrituras exigen rol administrador en el backend; los datos se filtran por la empresa del token.
const soloAdmin = [authenticate, requireAdminForWrites];

app.use("/autenticacion", authRoutes);
app.use("/usuarios", exceptMethods(["POST"], ...soloAdmin), userRoutes);
app.use("/clientes", ...soloAdmin, clientRoutes);
app.use("/contratos", ...soloAdmin, contractRoutes);
app.use("/auditoria", authenticate, auditRoutes);
app.use("/empresas", exceptMethods(["POST"], ...soloAdmin), empresasRoutes);
app.use("/roles", ...soloAdmin, rolesRoutes);
app.use("/empresa-usuarios", ...soloAdmin, empresaUsuariosRoutes);
app.use("/metricas", authenticate, metricasRoutes);

const openapi = require("./openapi.json");
app.use("/docs", swaggerUi.serve, swaggerUi.setup(openapi));
app.get("/openapi.json", (req, res) => {
  res.json(openapi);
});

app.get("/", (req, res) => {
  res.json({ name: "Atlas", status: "ok" });
});

const PORT = process.env.PORT || 3000;
migrarContrasenasLegadas()
  .catch((err) => console.error("Migración de contraseñas:", err.message))
  .finally(() => {
    app.listen(PORT, () => {
      console.log(`Atlas API escuchando en puerto ${PORT}`);
    });
  });
