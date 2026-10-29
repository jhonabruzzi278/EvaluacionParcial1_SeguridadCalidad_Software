// PT-PERF-003 — estabilidad con 200 usuarios concurrentes (NFR-PERF-3). Rampa a 200 VUs y sostenido; total 5 min.
// Uso:  k6 run -e API=http://localhost:4450 crud_200vu.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const API = __ENV.API || 'http://localhost:4450';
const JSON_H = { 'Content-Type': 'application/json' };

export const options = {
  stages: [{ duration: '1m', target: 200 }, { duration: '4m', target: 200 }],
  thresholds: { http_req_failed: ['rate<0.01'] },
};

export function setup() {
  const r = http.post(`${API}/autenticacion/login`, JSON.stringify({ nombre_usuario: 'admin', password: 'admin' }), { headers: JSON_H });
  return { token: r.json('token') };
}

export default function (data) {
  const h = { headers: { ...JSON_H, Authorization: `Bearer ${data.token}` } };
  const correo = `k6c-${__VU}-${__ITER}-${Date.now()}@atlasfake.com`;
  const r = http.get(`${API}/clientes`, h);
  check(r, { 'listar 200': (x) => x.status === 200 });
  const c = http.post(`${API}/clientes`, JSON.stringify({ nombre: `k6c ${__VU}-${__ITER}`, correo }), h);
  check(c, { 'crear 201': (x) => x.status === 201 });
  if (c.status === 201) http.del(`${API}/clientes/${c.json('id')}`, null, h);
  sleep(1);
}
