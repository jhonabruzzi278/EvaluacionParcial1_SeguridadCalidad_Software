// PT-PERF-001 / PT-PERF-003 — latencia CRUD de Atlas.
// Uso:  k6 run -e API=http://localhost:4450 crud_latencia.js
// Estado: escrito sin ejecutar (la máquina de desarrollo no tiene Docker ni k6).
import http from 'k6/http';
import { check, sleep } from 'k6';

const API = __ENV.API || 'http://localhost:4450';
const JSON_H = { 'Content-Type': 'application/json' };

export const options = {
  scenarios: {
    crud:  { executor: 'constant-vus', vus: 20, duration: '2m', exec: 'crud' },
    login: { executor: 'per-vu-iterations', vus: 1, iterations: 30, maxDuration: '5m', exec: 'login' },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{name:GET /clientes}':     ['p(95)<300'],
    'http_req_duration{name:POST /clientes}':    ['p(95)<300'],
    'http_req_duration{name:PUT /clientes}':     ['p(95)<300'],
    'http_req_duration{name:DELETE /clientes}':  ['p(95)<300'],
    'http_req_duration{name:POST /login}':       ['p(95)<300'],
  },
};

export function setup() {
  const r = http.post(`${API}/autenticacion/login`,
    JSON.stringify({ nombre_usuario: 'admin', password: 'admin' }), { headers: JSON_H });
  return { token: r.json('token') };
}

export function login() {
  const r = http.post(`${API}/autenticacion/login`,
    JSON.stringify({ nombre_usuario: 'admin', password: 'admin' }),
    { headers: JSON_H, tags: { name: 'POST /login' } });
  check(r, { 'login 200': (x) => x.status === 200 });
}

export function crud(data) {
  const h = { headers: { ...JSON_H, Authorization: `Bearer ${data.token}` } };
  const correo = `k6-${__VU}-${__ITER}-${Date.now()}@atlasfake.com`;

  http.get(`${API}/clientes`, { ...h, tags: { name: 'GET /clientes' } });

  const c = http.post(`${API}/clientes`,
    JSON.stringify({ nombre: `Cliente k6 ${__VU}-${__ITER}`, correo }),
    { ...h, tags: { name: 'POST /clientes' } });
  if (!check(c, { 'crear 201': (x) => x.status === 201 })) return;
  const id = c.json('id');

  http.put(`${API}/clientes/${id}`,
    JSON.stringify({ nombre: `Cliente k6 editado ${id}`, correo }),
    { ...h, tags: { name: 'PUT /clientes' } });
  http.del(`${API}/clientes/${id}`, null, { ...h, tags: { name: 'DELETE /clientes' } });
  sleep(1);
}
