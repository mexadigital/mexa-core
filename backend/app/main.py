<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Mexa Digital</title>

<style>
body{margin:0;font-family:Arial;background:#0f172a;color:white}
header{padding:16px;background:#020617;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}
header h2{margin:0}
button{padding:8px 12px;border:none;border-radius:8px;background:#2563eb;color:white;cursor:pointer;font-weight:bold}
button:hover{opacity:.9}
.danger{background:#dc2626}
.green{background:#16a34a}
.gray{background:#475569}
.orange{background:#f59e0b;color:#111827}
.container{max-width:980px;margin:auto;padding:18px}
.card{background:#111827;padding:12px;border-radius:12px;margin-bottom:10px;border:1px solid #1f2937}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
input,select,textarea{width:100%;padding:9px;margin:5px 0;background:#020617;color:white;border:1px solid #374151;border-radius:8px;box-sizing:border-box}
textarea{min-height:70px;resize:vertical}
.hidden{display:none}
#login{max-width:400px;margin:80px auto}
.status{color:#93c5fd;font-size:13px}
h3{margin-top:28px;margin-bottom:10px}
.mov{border-left:4px solid #dc2626}
.entrada{border-left:4px solid #16a34a}
.traspaso{border-left:4px solid #f59e0b}
.vale{border-left:4px solid #38bdf8}
.valeCerrado{border-left:4px solid #22c55e}
.valeParcial{border-left:4px solid #f59e0b}
.card:hover{outline:1px solid #2563eb}
.ubicacionActiva{outline:2px solid #22c55e}
.resumenUbicacion{background:#020617;padding:12px;border-radius:12px;margin-bottom:14px;border:1px solid #1f2937}
.small{font-size:13px;color:#cbd5e1}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.badge{display:inline-block;background:#020617;border:1px solid #334155;padding:3px 8px;border-radius:999px;font-size:12px;color:#cbd5e1;margin-top:4px}
.badgeBlue{border-color:#38bdf8;color:#bae6fd}
.badgeGreen{border-color:#22c55e;color:#bbf7d0}
.badgeOrange{border-color:#f59e0b;color:#fed7aa}
.badgeRed{border-color:#ef4444;color:#fecaca}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:15px}
.kpi{background:#020617;border:1px solid #1f2937;border-radius:12px;padding:12px}
.kpi b{font-size:24px}
.table{width:100%;border-collapse:collapse}
.table th,.table td{border-bottom:1px solid #1f2937;padding:8px;text-align:left;font-size:13px;vertical-align:top}
.table th{color:#93c5fd}
hr{border:none;border-top:1px solid #1f2937;margin:14px 0}
.detalleVale{background:#020617;border:1px solid #1f2937;border-radius:10px;padding:10px;margin-top:8px}
.liberacionBox{background:#020617;border:1px solid #1f2937;border-radius:12px;padding:14px;margin-top:10px}
.liberacionLibre{border-color:#22c55e;box-shadow:0 0 0 1px rgba(34,197,94,.25)}
.liberacionNo{border-color:#ef4444;box-shadow:0 0 0 1px rgba(239,68,68,.25)}
.liberacionSin{border-color:#38bdf8;box-shadow:0 0 0 1px rgba(56,189,248,.25)}
.tituloLiberacion{font-size:24px;font-weight:bold;margin-bottom:8px}
.btnRow{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}


/* =========================
   PANTALLA SPOOLS
========================= */
.spoolsShell{display:grid;grid-template-columns:245px 1fr;gap:14px;margin-bottom:24px}
.spoolsSidebar{background:#020617;border:1px solid #1f2937;border-radius:14px;padding:14px;height:fit-content}
.spoolsSidebar h3{margin:0 0 12px}
.treeRoot{font-weight:bold;color:#e2e8f0;margin-bottom:10px}
.treeArea{color:#4ade80;font-weight:bold;margin:10px 0 6px}
.treeItem{padding:8px 10px;margin:4px 0;border-radius:8px;background:#0f172a;border:1px solid #1f2937;cursor:pointer;font-size:13px}
.treeItem:hover,.treeItem.active{border-color:#22c55e;background:#052e16}
.spoolsMain{min-width:0}
.spoolsHero{background:linear-gradient(135deg,#111827,#0b1220);border:1px solid #1f2937;border-radius:14px;padding:16px;margin-bottom:12px}
.spoolsHero h2{margin:0 0 4px}
.spoolsSearch{display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:8px;align-items:end;margin-top:14px}
.spoolsKpis{display:grid;grid-template-columns:repeat(4,minmax(135px,1fr));gap:10px;margin:12px 0}
.spoolsKpi{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:12px}
.spoolsKpi strong{display:block;font-size:25px;margin-top:4px}
.spoolsTableWrap{overflow:auto;background:#111827;border:1px solid #1f2937;border-radius:12px}
.spoolsTable{width:100%;border-collapse:collapse;min-width:850px}
.spoolsTable th,.spoolsTable td{padding:10px;border-bottom:1px solid #1f2937;text-align:left;font-size:13px}
.spoolsTable th{color:#93c5fd;background:#0b1220;position:sticky;top:0}
.spoolsAction{padding:5px 8px;font-size:12px;margin-right:4px}
.sectionTitleRow{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:14px 0 8px}
.sectionTitleRow h3{margin:0}
.spoolsEmpty{padding:18px;color:#94a3b8;text-align:center}
@media(max-width:900px){
  .spoolsShell{grid-template-columns:1fr}
  .spoolsSidebar{display:none}
  .spoolsSearch{grid-template-columns:1fr 1fr}
  .spoolsKpis{grid-template-columns:1fr 1fr}
}
@media(max-width:560px){
  .spoolsSearch,.spoolsKpis{grid-template-columns:1fr}
}

@media(max-width:720px){
  .row,.row3{grid-template-columns:1fr}
  header{gap:10px;align-items:flex-start;flex-direction:column}
}
</style>
</head>

<body>

<header>
  <h2>Mexa Digital</h2>
  <div>
    <button onclick="cargarTodo()">Actualizar</button>
    <button class="danger" onclick="cerrarSesion()">Salir</button>
  </div>
</header>

<div id="login" class="container">
  <h2>Login</h2>
  <input id="email" value="admin.ica@mexa.com">
  <input id="password" type="password" value="123456">
  <button onclick="login()">Entrar</button>
  <p id="msg"></p>
</div>

<div id="app" class="container hidden">

  <p id="estado" class="status"></p>


  <section id="pantallaSpools">
    <div class="spoolsShell">
      <aside class="spoolsSidebar">
        <h3>Estructura</h3>
        <div class="treeRoot">🏭 Almacén General</div>
        <div class="treeArea">▾ Área: Spools</div>
        <div id="arbolSpools"></div>
      </aside>

      <main class="spoolsMain">
        <div class="spoolsHero">
          <h2>Almacén General — Área Spools</h2>
          <div class="small">Consulta herramientas y equipos distribuidos entre naves, contenedores, patios y zonas internas.</div>

          <div class="spoolsSearch">
            <div>
              <label class="small">Herramienta, equipo o código</label>
              <input id="spoolsBuscar" placeholder="Ej. HYTORC, perica, B12M..." oninput="renderPantallaSpools()">
            </div>
            <div>
              <label class="small">Ubicación</label>
              <select id="spoolsUbicacion" onchange="renderPantallaSpools()"></select>
            </div>
            <div>
              <label class="small">Tipo</label>
              <select id="spoolsTipo" onchange="renderPantallaSpools()">
                <option value="">Todos</option>
                <option value="herramienta">Herramienta</option>
                <option value="equipo_industrial">Equipo industrial</option>
                <option value="consumible">Consumible</option>
                <option value="epp">EPP</option>
                <option value="material">Material</option>
              </select>
            </div>
            <button class="green" onclick="renderPantallaSpools()">Buscar</button>
          </div>
        </div>

        <div class="spoolsKpis">
          <div class="spoolsKpi"><span class="small">Naves / contenedores</span><strong id="spKUbicaciones">0</strong></div>
          <div class="spoolsKpi"><span class="small">Productos registrados</span><strong id="spKProductos">0</strong></div>
          <div class="spoolsKpi"><span class="small">Existencia total</span><strong id="spKStock">0</strong></div>
          <div class="spoolsKpi"><span class="small">Traspasos registrados</span><strong id="spKTraspasos">0</strong></div>
        </div>

        <div class="sectionTitleRow">
          <h3>Inventario del área Spools</h3>
          <button class="gray" onclick="limpiarFiltrosSpools()">Limpiar filtros</button>
        </div>
        <div class="spoolsTableWrap">
          <table class="spoolsTable">
            <thead>
              <tr>
                <th>Código</th><th>Herramienta / equipo</th><th>Tipo</th><th>Ubicación</th><th>Responsable</th><th>Disponible</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody id="tablaSpools"></tbody>
          </table>
        </div>
      </main>
    </div>
  </section>


  <div class="kpis">
    <div class="kpi"><span class="small">Ubicaciones</span><br><b id="kUbicaciones">0</b></div>
    <div class="kpi"><span class="small">Productos</span><br><b id="kProductos">0</b></div>
    <div class="kpi"><span class="small">Stock total real</span><br><b id="kStock">0</b></div>
    <div class="kpi"><span class="small">Movimientos</span><br><b id="kMovimientos">0</b></div>
    <div class="kpi"><span class="small">Vales abiertos</span><br><b id="kVales">0</b></div>
  </div>

  <h3>Ubicaciones</h3>
  <div id="grid" class="grid"></div>
  <div id="productosUbicacion" class="resumenUbicacion hidden"></div>

  <h3>Inventario real por ubicación</h3>
  <div id="inventarioUbicacion"></div>

  <div class="soloAdmin">
    <h3>Crear ubicación</h3>
    <input id="uNombre" placeholder="Nombre de ubicación">

    <select id="uTipo">
      <option value="contenedor">Contenedor</option>
      <option value="almacen_satelite">Almacén satélite</option>
      <option value="nave">Nave</option>
      <option value="almacen_abierto">Almacén a cielo abierto</option>
      <option value="patio">Patio</option>
    </select>

    <input id="uResp" placeholder="Responsable / mero mero">
    <input id="uEmpleado" placeholder="Número de empleado">
    <button onclick="crearUbicacion()">Guardar ubicación</button>
  </div>

  <div class="soloAdmin">
    <h3>Crear producto</h3>
    <input id="pNombre" placeholder="Nombre">
    <input id="pCodigo" placeholder="Código / Nº Serie">
    <input id="pCant" type="number" value="1">

    <select id="pTipo">
      <option value="herramienta">Herramienta</option>
      <option value="consumible">Consumible</option>
      <option value="epp">EPP</option>
      <option value="material">Material</option>
      <option value="equipo_industrial">Equipo industrial</option>
    </select>

    <select id="pUbicacion"></select>
    <button onclick="crearProducto()">Guardar producto</button>
  </div>

  <h3>Registrar salida</h3>
  <select id="sInventario"></select>
  <input id="sCantidad" type="number" value="1" placeholder="Cantidad">
  <input id="sRecibe" placeholder="Quién recibe">
  <input id="sNota" placeholder="Nota / frente de trabajo">
  <button class="danger" onclick="registrarSalida()">Registrar salida</button>

  <h3>Traspaso entre ubicaciones</h3>
  <select id="tProducto"></select>

  <div class="row">
    <select id="tOrigen"></select>
    <select id="tDestino"></select>
  </div>

  <input id="tCantidad" type="number" value="1" placeholder="Cantidad">
  <input id="tResponsable" placeholder="Quién autoriza / mueve">
  <input id="tNota" placeholder="Nota del traspaso">
  <button class="green" onclick="registrarTraspaso()">Registrar traspaso</button>

  <h3>Vales de resguardo</h3>

  <div class="card vale">
    <h3 style="margin-top:0">Crear vale</h3>

    <div class="row">
      <input id="vNumeroFisico" placeholder="Número físico del vale, ejemplo 1587">
      <input id="vFotoUrl" placeholder="URL foto del vale">
    </div>

    <div class="row">
      <input id="vEmpleado" placeholder="Empleado responsable">
      <input id="vNumeroEmpleado" placeholder="Número de empleado">
    </div>

    <div class="row">
      <input id="vPuesto" placeholder="Puesto">
      <input id="vArea" placeholder="Área / frente">
    </div>

    <div class="row">
      <input id="vUbicacionOrigen" placeholder="Ubicación origen, ejemplo M-06">
      <input id="vUbicacionFisica" value="Carpeta A / A0001-A0050" placeholder="Dónde guardarás el papel físico">
    </div>

    <textarea id="vNota" placeholder="Nota general del vale"></textarea>

    <h4>Herramientas / artículos del vale</h4>
    <p class="small">Captura rápido lo que dice el vale físico. No necesita existir en inventario. Puedes agregar todos los renglones que necesites.</p>

    <div id="contenedorDetallesVale"></div>

    <button class="gray" type="button" onclick="agregarRenglonVale()">+ Agregar herramienta</button>
    <button class="green" onclick="crearValeResguardo()">Crear vale de resguardo</button>
  </div>

  <div class="card">
    <h3 style="margin-top:0">Buscar vales</h3>
    <div class="row">
      <input id="buscarVale" placeholder="Buscar por nombre, número empleado, folio A0001, vale físico, área">
      <button onclick="buscarVales()">Buscar</button>
    </div>
    <button class="gray" onclick="cargarValesAbiertos()">Ver abiertos / parciales / cerrados pendientes</button>
    <button class="gray" onclick="cargarVales()">Ver todos</button>
  </div>

  <div class="card">
    <h3 style="margin-top:0">Reporte de bajas y pendientes por empleado</h3>
    <p class="small">Busca por nombre, número de empleado, folio del sistema o número físico del vale. El sistema dirá si puede salir libre o si debe herramientas.</p>

    <div class="row">
      <input id="buscarReporteEmpleado" placeholder="Ejemplo: Badillo, 12345, A0001 o VF-001">
      <button class="orange" onclick="buscarReporteEmpleado()">Revisar liberación</button>
    </div>

    <div id="resultadoReporteEmpleado"></div>
  </div>

  <h3>Vales capturados</h3>
  <div id="valesResguardo"></div>

  <h3>Productos dados de alta</h3>
  <div id="productos"></div>

  <h3>Historial de movimientos</h3>
  <div id="movimientos"></div>

</div>

<script>
const API="https://mexa-core-1.onrender.com";

let ubicacionesPantalla=[];
let productosPantalla=[];
let movimientosPantalla=[];
let inventarioResumen=[];
let valesPantalla=[];
let ubicacionSeleccionada="";
let contadorRenglonesVale=0;

function tokenActual(){
  return localStorage.getItem("token") || localStorage.getItem("mexa_token") || "";
}

function guardarToken(token){
  localStorage.setItem("token", token);
  localStorage.setItem("mexa_token", token);
}

function headers(){
  return {
    "Content-Type":"application/json",
    "Authorization":"Bearer "+tokenActual()
  };
}

function setEstado(txt){
  const estado=document.getElementById("estado");
  if(estado) estado.innerText=txt;
}

/* =========================
   PERMISOS POR ROL
========================= */
function leerPayloadToken(){
  const token = tokenActual();

  if(!token || !token.includes(".")){
    return {};
  }

  try{
    const payload = token.split(".")[1];
    const normalizado = payload.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(normalizado));
  }catch(e){
    return {};
  }
}

function obtenerRolUsuario(){
  const payload = leerPayloadToken();

  return (
    payload.rol ||
    payload.role ||
    payload.tipo ||
    payload.user_role ||
    ""
  );
}

function obtenerEmailUsuario(){
  const payload = leerPayloadToken();

  return (
    payload.sub ||
    payload.email ||
    payload.usuario ||
    ""
  );
}

function esAdmin(){
  const rol = obtenerRolUsuario();
  const email = obtenerEmailUsuario();

  if(rol === "admin" || rol === "superadmin"){
    return true;
  }

  if(email === "admin.ica@mexa.com"){
    return true;
  }

  return false;
}

function aplicarPermisos(){
  const admin = esAdmin();

  document.querySelectorAll(".soloAdmin").forEach(el=>{
    if(admin){
      el.classList.remove("hidden");
    }else{
      el.classList.add("hidden");
    }
  });

  const email = obtenerEmailUsuario();
  const rol = obtenerRolUsuario() || (admin ? "admin" : "usuario");

  setEstado(`Sesión: ${email || "usuario"} | Rol: ${rol}`);
}

function bloquearSiNoAdmin(){
  if(!esAdmin()){
    alert("No tienes permiso para esta acción");
    return true;
  }

  return false;
}

/* =========================
   LOCAL STORAGE DEMO
========================= */
function getLocalUbicaciones(){
  return JSON.parse(localStorage.getItem("mexa_ubicaciones_demo") || "[]");
}

function setLocalUbicaciones(data){
  localStorage.setItem("mexa_ubicaciones_demo", JSON.stringify(data));
}

function getLocalProductos(){
  return JSON.parse(localStorage.getItem("mexa_productos_demo") || "[]");
}

function setLocalProductos(data){
  localStorage.setItem("mexa_productos_demo", JSON.stringify(data));
}

function getLocalMovimientos(){
  return JSON.parse(localStorage.getItem("mexa_movimientos_demo") || "[]");
}

function setLocalMovimientos(data){
  localStorage.setItem("mexa_movimientos_demo", JSON.stringify(data));
}

/* =========================
   HELPERS
========================= */
function unirPorNombre(base, extras){
  const mapa={};

  [...extras, ...base].forEach(x=>{
    if(!x || !x.nombre) return;

    if(!mapa[x.nombre]){
      mapa[x.nombre]=x;
      return;
    }

    if(x.id && !mapa[x.nombre].id){
      mapa[x.nombre]=x;
    }
  });

  return Object.values(mapa);
}

function unirPorCodigo(base, extras){
  const mapa={};

  [...base,...extras].forEach(x=>{
    if(x && x.codigo) mapa[x.codigo]=x;
  });

  return Object.values(mapa);
}

function nombreProductoMovimiento(m){
  if(m.producto_nombre) return m.producto_nombre;
  if(m.producto) return m.producto;
  if(m.nombre) return m.nombre;

  let producto=productosPantalla.find(p=>String(p.id)===String(m.producto_id));
  if(producto) return producto.nombre;

  if(m.codigo) return m.codigo;
  return "-";
}

function nombreUbicacionPorId(id){
  let inv=inventarioResumen.find(x=>String(x.ubicacion_id)===String(id));
  if(inv) return inv.ubicacion;

  let u=ubicacionesPantalla.find(x=>String(x.id)===String(id));
  if(u) return u.nombre;

  return "-";
}

function unirMovimientosSinDuplicados(locales, backend){
  const mapa={};

  [...backend, ...locales].forEach(m=>{
    const nombre=nombreProductoMovimiento(m);

    const clave=[
      m.id || "",
      m.tipo || "",
      nombre || "",
      m.cantidad || "",
      m.recibe || "",
      m.nota || "",
      m.ubicacion_id || m.ubicacion || m.ubicacion_salida || "",
      m.fecha || m.created_at || ""
    ].join("|");

    if(!mapa[clave]){
      mapa[clave]=m;
    }
  });

  return Object.values(mapa);
}

function badgeEstadoVale(estado){
  if(estado==="cerrado") return `<span class="badge badgeOrange">Cerrado con pendiente</span>`;
  if(estado==="parcial") return `<span class="badge badgeOrange">Parcial</span>`;
  if(estado==="devuelto") return `<span class="badge badgeGreen">Devuelto completo</span>`;
  if(estado==="cancelado") return `<span class="badge badgeRed">Cancelado</span>`;
  return `<span class="badge badgeBlue">Abierto</span>`;
}

function claseVale(estado){
  if(estado==="devuelto") return "valeCerrado";
  if(estado==="cerrado") return "valeParcial";
  if(estado==="parcial") return "valeParcial";
  return "vale";
}

/* =========================
   LOGIN ROBUSTO
========================= */
async function login(){
  const email=document.getElementById("email").value.trim();
  const password=document.getElementById("password").value.trim();
  const msg=document.getElementById("msg");

  msg.innerText="Entrando...";

  localStorage.removeItem("token");
  localStorage.removeItem("mexa_token");

  const intentos=[
    {
      ruta:"/auth/login",
      tipo:"json_email",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({email:email,password:password})
    },
    {
      ruta:"/auth/login",
      tipo:"json_username",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({username:email,password:password})
    },
    {
      ruta:"/auth/login",
      tipo:"form_username",
      headers:{"Content-Type":"application/x-www-form-urlencoded"},
      body:new URLSearchParams({
        username:email,
        password:password
      })
    },
    {
      ruta:"/auth/auth/login",
      tipo:"json_email",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({email:email,password:password})
    },
    {
      ruta:"/auth/auth/login",
      tipo:"form_username",
      headers:{"Content-Type":"application/x-www-form-urlencoded"},
      body:new URLSearchParams({
        username:email,
        password:password
      })
    }
  ];

  let errores=[];

  for(let intento of intentos){
    try{
      let res=await fetch(API+intento.ruta,{
        method:"POST",
        headers:intento.headers,
        body:intento.body
      });

      let texto=await res.text();
      let data={};

      try{
        data=JSON.parse(texto);
      }catch(e){
        data={raw:texto};
      }

      const token =
        data.access_token ||
        data.token ||
        data.accessToken ||
        data.jwt ||
        data.bearer_token;

      if(res.ok && token){
        guardarToken(token);

        document.getElementById("login").classList.add("hidden");
        document.getElementById("app").classList.remove("hidden");

        msg.innerText="Login correcto. Cargando datos...";

        aplicarPermisos();
        await cargarTodo();
        aplicarPermisos();

        msg.innerText="";
        return;
      }

      errores.push(`${intento.ruta} (${intento.tipo}) → ${res.status}: ${texto}`);

    }catch(e){
      errores.push(`${intento.ruta} (${intento.tipo}) → FALLÓ: ${e.message}`);
    }
  }

  console.error("Errores login:", errores);
  msg.innerText="Error login. Abre F12 → Console y revisa 'Errores login'.";
  alert("Error login. Abre F12 → Console y revisa 'Errores login'.");
}

function cerrarSesion(){
  localStorage.removeItem("token");
  localStorage.removeItem("mexa_token");
  location.reload();
}


/* =========================
   DASHBOARD ÁREA SPOOLS
========================= */
function inventarioSpoolsNormalizado(){
  if(inventarioResumen.length){
    return inventarioResumen.map(x=>{
      const producto=productosPantalla.find(p=>String(p.id)===String(x.producto_id)) || {};
      const ubicacion=ubicacionesPantalla.find(u=>String(u.id)===String(x.ubicacion_id)) || {};
      return {
        producto_id:x.producto_id,
        ubicacion_id:x.ubicacion_id,
        codigo:x.codigo || producto.codigo || "-",
        nombre:x.producto || producto.nombre || "-",
        tipo:producto.tipo || "-",
        ubicacion:x.ubicacion || ubicacion.nombre || "Sin ubicación",
        responsable:ubicacion.responsable || "Sin responsable",
        cantidad:Number(x.cantidad || 0)
      };
    });
  }

  return productosPantalla.map(p=>{
    const ubicacion=ubicacionesPantalla.find(u=>u.nombre===p.ubicacion) || {};
    return {
      producto_id:p.id,
      ubicacion_id:ubicacion.id || null,
      codigo:p.codigo || "-",
      nombre:p.nombre || "-",
      tipo:p.tipo || "-",
      ubicacion:p.ubicacion || "Sin ubicación",
      responsable:ubicacion.responsable || "Sin responsable",
      cantidad:Number(p.cantidad || 0)
    };
  });
}

function prepararFiltrosSpools(){
  const select=document.getElementById("spoolsUbicacion");
  if(!select) return;

  const actual=select.value;
  select.innerHTML='<option value="">Todas</option>';
  ubicacionesPantalla.forEach(u=>{
    select.innerHTML+=`<option value="${u.nombre}">${u.nombre}</option>`;
  });
  if([...select.options].some(o=>o.value===actual)) select.value=actual;
}

function seleccionarUbicacionSpools(nombre){
  const select=document.getElementById("spoolsUbicacion");
  if(select) select.value=nombre;
  renderPantallaSpools();
}

function limpiarFiltrosSpools(){
  const q=document.getElementById("spoolsBuscar");
  const u=document.getElementById("spoolsUbicacion");
  const t=document.getElementById("spoolsTipo");
  if(q) q.value="";
  if(u) u.value="";
  if(t) t.value="";
  renderPantallaSpools();
}

function cargarProductoEnTraspaso(productoId,ubicacionId){
  const p=document.getElementById("tProducto");
  const o=document.getElementById("tOrigen");
  if(p) p.value=String(productoId);
  if(o && ubicacionId) o.value=String(ubicacionId);
  document.getElementById("tCantidad")?.focus();
  document.getElementById("tProducto")?.scrollIntoView({behavior:"smooth",block:"center"});
}

function mostrarDetalleSpools(productoId,ubicacionId){
  const x=inventarioSpoolsNormalizado().find(i=>String(i.producto_id)===String(productoId) && String(i.ubicacion_id)===String(ubicacionId));
  if(!x) return;
  alert(`${x.nombre}
Código: ${x.codigo}
Tipo: ${x.tipo}
Ubicación: ${x.ubicacion}
Responsable: ${x.responsable}
Disponible: ${x.cantidad}`);
}

function renderPantallaSpools(){
  const tabla=document.getElementById("tablaSpools");
  const arbol=document.getElementById("arbolSpools");
  if(!tabla || !arbol) return;

  prepararFiltrosSpools();

  const q=(document.getElementById("spoolsBuscar")?.value || "").trim().toLowerCase();
  const ubicacionFiltro=document.getElementById("spoolsUbicacion")?.value || "";
  const tipoFiltro=document.getElementById("spoolsTipo")?.value || "";
  const datos=inventarioSpoolsNormalizado();

  arbol.innerHTML=ubicacionesPantalla.length
    ? ubicacionesPantalla.map(u=>`<div class="treeItem ${ubicacionFiltro===u.nombre ? "active" : ""}" onclick='seleccionarUbicacionSpools(${JSON.stringify(u.nombre)})'>▣ ${u.nombre}</div>`).join("")
    : '<div class="small">Sin ubicaciones registradas</div>';

  const filtrados=datos.filter(x=>{
    const coincideQ=!q || `${x.nombre} ${x.codigo} ${x.ubicacion} ${x.responsable}`.toLowerCase().includes(q);
    const coincideU=!ubicacionFiltro || x.ubicacion===ubicacionFiltro;
    const coincideT=!tipoFiltro || x.tipo===tipoFiltro;
    return coincideQ && coincideU && coincideT;
  });

  tabla.innerHTML=filtrados.length
    ? filtrados.map(x=>`<tr>
        <td><b>${x.codigo}</b></td>
        <td>${x.nombre}</td>
        <td>${x.tipo}</td>
        <td>${x.ubicacion}</td>
        <td>${x.responsable}</td>
        <td><span class="badge ${x.cantidad>0 ? "badgeGreen" : "badgeRed"}">${x.cantidad}</span></td>
        <td>
          <button class="spoolsAction gray" onclick="mostrarDetalleSpools(${x.producto_id},${x.ubicacion_id || 'null'})">Ver</button>
          ${x.cantidad>0 && x.ubicacion_id ? `<button class="spoolsAction green" onclick="cargarProductoEnTraspaso(${x.producto_id},${x.ubicacion_id})">Mover</button>` : ""}
        </td>
      </tr>`).join("")
    : '<tr><td colspan="7" class="spoolsEmpty">No hay resultados para estos filtros.</td></tr>';

  const stock=datos.reduce((s,x)=>s+x.cantidad,0);
  const traspasos=movimientosPantalla.filter(m=>m.tipo==="traspaso").length;
  document.getElementById("spKUbicaciones").innerText=ubicacionesPantalla.length;
  document.getElementById("spKProductos").innerText=new Set(datos.map(x=>x.producto_id || x.codigo)).size;
  document.getElementById("spKStock").innerText=stock;
  document.getElementById("spKTraspasos").innerText=traspasos;
}

/* =========================
   CARGA GENERAL
========================= */
async function cargarTodo(){
  setEstado("Cargando datos...");

  let ubicacionesBackend=[];
  let productosBackend=[];
  let movimientosBackend=[];
  let inventarioBackend=[];

  try{
    let resU=await fetch(API+"/ubicaciones/ubicaciones/?t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(resU.ok) ubicacionesBackend=await resU.json();
  }catch(e){}

  try{
    let resP=await fetch(API+"/productos/productos/?t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(resP.ok) productosBackend=await resP.json();
  }catch(e){}

  try{
    let resI=await fetch(API+"/inventario-ubicaciones/resumen?t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(resI.ok) inventarioBackend=await resI.json();
  }catch(e){}

  try{
    let resM=await fetch(API+"/movimientos/movimientos/?t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(resM.ok) movimientosBackend=await resM.json();
  }catch(e){}

  ubicacionesPantalla=unirPorNombre(ubicacionesBackend,getLocalUbicaciones());
  productosPantalla=unirPorCodigo(productosBackend,getLocalProductos());
  inventarioResumen=inventarioBackend || [];
  movimientosPantalla=unirMovimientosSinDuplicados(getLocalMovimientos(),movimientosBackend);

  await cargarValesAbiertos(false);

  renderKpis();
  renderUbicaciones();
  renderInventarioPorUbicacion();
  renderProductos();
  renderSelectSalida();
  renderSelectTraspaso();
  renderMovimientos();
  renderVales();
  renderPantallaSpools();

  aplicarPermisos();
}

/* =========================
   RENDERS
========================= */
function renderKpis(){
  const stockReal=inventarioResumen.length
    ? inventarioResumen.reduce((s,p)=>s+Number(p.cantidad || 0),0)
    : productosPantalla.reduce((s,p)=>s+Number(p.cantidad || 0),0);

  const valesAbiertos=valesPantalla.filter(v=>
    v.estado_vale==="abierto" ||
    v.estado_vale==="parcial" ||
    v.estado_vale==="cerrado"
  ).length;

  document.getElementById("kUbicaciones").innerText=ubicacionesPantalla.length;
  document.getElementById("kProductos").innerText=productosPantalla.length;
  document.getElementById("kStock").innerText=stockReal;
  document.getElementById("kMovimientos").innerText=movimientosPantalla.length;
  document.getElementById("kVales").innerText=valesAbiertos;
}

function renderUbicaciones(){
  let grid=document.getElementById("grid");
  let select=document.getElementById("pUbicacion");

  grid.innerHTML="";
  select.innerHTML="";

  if(ubicacionesPantalla.length===0){
    grid.innerHTML="<p>No hay ubicaciones cargadas</p>";
    select.innerHTML="<option value=''>Sin ubicaciones</option>";
    return;
  }

  ubicacionesPantalla.forEach(u=>{
    let total=0;

    if(inventarioResumen.length){
      total=inventarioResumen
        .filter(x=>String(x.ubicacion_id)===String(u.id) || x.ubicacion===u.nombre)
        .reduce((s,x)=>s+Number(x.cantidad || 0),0);
    }else{
      total=productosPantalla
        .filter(p=>p.ubicacion===u.nombre)
        .reduce((s,p)=>s+Number(p.cantidad || 0),0);
    }

    grid.innerHTML+=`
      <div class="card ${ubicacionSeleccionada===u.nombre ? "ubicacionActiva" : ""}" onclick="mostrarProductosUbicacion(${JSON.stringify(u.nombre).replace(/"/g,'&quot;')})">
        <b>${u.nombre}</b><br>
        <span class="small">Tipo: ${u.tipo || "-"}</span><br>
        <span class="small">
          Responsable: ${u.responsable || "Sin responsable"}<br>
          Empleado: ${u.numero_empleado || "-"}
        </span><br>
        <span class="badge">Stock real: ${total}</span>
        <span class="badge">Clic para ver productos</span>
      </div>
    `;

    if(u.id){
      select.innerHTML+=`<option value="${u.id}" data-nombre="${u.nombre}">${u.nombre}</option>`;
    }
  });
}

function mostrarProductosUbicacion(nombre){
  ubicacionSeleccionada=nombre;

  let div=document.getElementById("productosUbicacion");
  let ubicacion=ubicacionesPantalla.find(u=>u.nombre===nombre);

  let productos=[];

  if(inventarioResumen.length){
    productos=inventarioResumen.filter(x=>x.ubicacion===nombre);
  }else{
    productos=productosPantalla.filter(p=>p.ubicacion===nombre);
  }

  div.classList.remove("hidden");

  if(productos.length===0){
    div.innerHTML=`
      <b>${nombre}</b><br>
      <span class="small">
        Responsable: ${ubicacion?.responsable || "Sin responsable"}<br>
        Empleado: ${ubicacion?.numero_empleado || "-"}
      </span><br>
      <span class="small">No hay productos en esta ubicación</span>
    `;
  }else{
    div.innerHTML=`
      <b>${nombre}</b><br>
      <span class="small">
        Responsable: ${ubicacion?.responsable || "Sin responsable"}<br>
        Empleado: ${ubicacion?.numero_empleado || "-"}
      </span><br><br>
      ${productos.map(p=>`
        <div class="small">• ${p.producto || p.nombre} — ${p.codigo || "-"} — Stock real: <b>${p.cantidad ?? 0}</b></div>
      `).join("")}
    `;
  }

  renderUbicaciones();
}

function renderInventarioPorUbicacion(){
  let div=document.getElementById("inventarioUbicacion");

  if(inventarioResumen.length===0){
    div.innerHTML=`
      <div class="card">
        <p>No hay inventario real por ubicación todavía.</p>
        <p class="small">Crea una entrada o registra un producto con stock para llenar esta tabla.</p>
      </div>
    `;
    return;
  }

  let filas=inventarioResumen.map(x=>`
    <tr>
      <td>${x.ubicacion || "-"}</td>
      <td>${x.tipo_ubicacion || "-"}</td>
      <td>${x.producto || "-"}</td>
      <td>${x.codigo || "-"}</td>
      <td><b>${x.cantidad ?? 0}</b></td>
    </tr>
  `);

  div.innerHTML=`
    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Ubicación</th>
            <th>Tipo ubicación</th>
            <th>Producto</th>
            <th>Código</th>
            <th>Cantidad real</th>
          </tr>
        </thead>
        <tbody>${filas.join("")}</tbody>
      </table>
    </div>
  `;
}

function renderProductos(){
  let div=document.getElementById("productos");

  if(productosPantalla.length===0){
    div.innerHTML="<p>No hay productos dados de alta todavía</p>";
    return;
  }

  div.innerHTML=productosPantalla.map(p=>{
    let stockReal=inventarioResumen
      .filter(x=>String(x.producto_id)===String(p.id))
      .reduce((s,x)=>s+Number(x.cantidad || 0),0);

    return `
      <div class="card">
        <b>${p.nombre}</b><br>
        <span class="small">Código / Nº Serie: ${p.codigo || "-"}</span><br>
        <span class="small">Tipo: ${p.tipo || "-"}</span><br>
        <span class="small">Ubicación original: ${p.ubicacion || "Sin ubicación"}</span><br>
        <span class="badge">Stock real: ${inventarioResumen.length ? stockReal : (p.cantidad ?? 0)}</span>
      </div>
    `;
  }).join("");
}

function renderSelectSalida(){
  let select=document.getElementById("sInventario");
  select.innerHTML="";

  if(inventarioResumen.length===0){
    select.innerHTML="<option value=''>Sin inventario real</option>";
    return;
  }

  inventarioResumen.forEach(x=>{
    select.innerHTML+=`
      <option value="${x.producto_id}|${x.ubicacion_id}">
        ${x.producto} | ${x.codigo} | ${x.ubicacion} | Stock: ${x.cantidad}
      </option>
    `;
  });
}

function renderSelectTraspaso(){
  let producto=document.getElementById("tProducto");
  let origen=document.getElementById("tOrigen");
  let destino=document.getElementById("tDestino");

  producto.innerHTML="";
  origen.innerHTML="";
  destino.innerHTML="";

  let productosParaTraspaso = [];

  if(inventarioResumen.length){
    const mapa = {};

    inventarioResumen.forEach(x=>{
      if(x.producto_id){
        mapa[x.producto_id] = {
          id: x.producto_id,
          nombre: x.producto,
          codigo: x.codigo
        };
      }
    });

    productosParaTraspaso = Object.values(mapa);
  }else{
    productosParaTraspaso = productosPantalla;
  }

  if(productosParaTraspaso.length===0){
    producto.innerHTML="<option value=''>Sin productos</option>";
  }else{
    productosParaTraspaso.forEach(p=>{
      producto.innerHTML+=`
        <option value="${p.id}">
          ${p.nombre} | ${p.codigo || "-"}
        </option>
      `;
    });
  }

  if(ubicacionesPantalla.length===0){
    origen.innerHTML="<option value=''>Sin ubicaciones</option>";
    destino.innerHTML="<option value=''>Sin ubicaciones</option>";
    return;
  }

  ubicacionesPantalla.forEach(u=>{
    if(u.id){
      origen.innerHTML+=`<option value="${u.id}">${u.nombre}</option>`;
      destino.innerHTML+=`<option value="${u.id}">${u.nombre}</option>`;
    }
  });
}

function renderMovimientos(){
  let div=document.getElementById("movimientos");

  if(movimientosPantalla.length===0){
    div.innerHTML="<p>No hay movimientos registrados todavía</p>";
    return;
  }

  div.innerHTML=movimientosPantalla
    .slice()
    .sort((a,b)=> new Date(b.created_at || b.fecha || 0) - new Date(a.created_at || a.fecha || 0))
    .map(m=>{
      let clase="mov";
      if(m.tipo==="entrada") clase="entrada";
      if(m.tipo==="traspaso") clase="traspaso";

      let ubicacionTexto=m.ubicacion || m.ubicacion_salida || nombreUbicacionPorId(m.ubicacion_id);

      return `
        <div class="card ${clase}">
          <b>${m.tipo || "salida"}</b> — ${m.cantidad || 0} de 
          <b>${nombreProductoMovimiento(m)}</b><br>
          <span class="small">Responsable / recibe: ${m.recibe || m.usuario || "Sin nombre"}</span><br>
          <span class="small">Ubicación: ${ubicacionTexto}</span><br>
          <span class="small">Nota: ${m.nota || "-"}</span><br>
          <span class="small">Fecha: ${m.created_at || m.fecha || "Ahora"}</span>
        </div>
      `;
    }).join("");
}

function renderVales(){
  let div=document.getElementById("valesResguardo");

  if(!div) return;

  if(valesPantalla.length===0){
    div.innerHTML=`
      <div class="card">
        <p>No hay vales capturados todavía.</p>
        <p class="small">Crea el primer vale físico y el sistema le dará folio A0001.</p>
      </div>
    `;
    renderKpis();
    return;
  }

  div.innerHTML=valesPantalla.map(v=>{
    let detalles=(v.detalles || []);

    let pendientes=detalles.filter(d=>Number(d.cantidad_devuelta || 0) < Number(d.cantidad_entregada || 0));

    let detalleHtml=detalles.map(d=>{
      let entregada=Number(d.cantidad_entregada || 0);
      let devuelta=Number(d.cantidad_devuelta || 0);
      let falta=entregada-devuelta;

      return `
        <div class="detalleVale">
          <b>${d.herramienta_nombre || "-"}</b><br>
          <span class="small">
            Entregado: ${entregada} |
            Devuelto: ${devuelta} |
            Falta: <b>${falta}</b> |
            Estado: ${d.estado || "-"}
          </span><br>
          <span class="small">Obs: ${d.observacion || "-"}</span>

          ${falta > 0 ? `
            <div class="row" style="margin-top:8px">
              <input id="dev_${v.id}_${d.id}" type="number" value="${falta}" min="1" max="${falta}">
              <button class="green" onclick="registrarDevolucion(${v.id},${d.id})">Registrar devolución</button>
            </div>
          ` : `<span class="badge badgeGreen">Completo</span>`}
        </div>
      `;
    }).join("");

    let pendientesTexto=pendientes.length
      ? pendientes.map(d=>{
          let falta=Number(d.cantidad_entregada || 0)-Number(d.cantidad_devuelta || 0);
          return `${d.herramienta_nombre} (${falta})`;
        }).join(", ")
      : "Sin pendientes";

    let foto=v.foto_url
      ? `<a href="${v.foto_url}" target="_blank" style="color:#93c5fd">Ver foto</a>`
      : `<span class="small">Sin foto URL</span>`;

    return `
      <div class="card ${claseVale(v.estado_vale)}">
        <b>${v.folio_sistema}</b> ${badgeEstadoVale(v.estado_vale)}<br>
        <span class="small">Vale físico: ${v.numero_vale_fisico || "-"}</span><br>
        <span class="small">Empleado: <b>${v.empleado_recibe || "-"}</b> | No. empleado: ${v.numero_empleado || "-"}</span><br>
        <span class="small">Puesto: ${v.puesto || "-"} | Área/frente: ${v.area_frente || "-"}</span><br>
        <span class="small">Ubicación origen: ${v.ubicacion_origen || "-"}</span><br>
        <span class="small">Papel físico: <b>${v.ubicacion_fisica_vale || "-"}</b> | Archivo: ${v.estado_archivo_fisico || "-"}</span><br>
        <span class="small">Fecha: ${v.fecha_entrega || "-"}</span><br>
        <span class="small">Nota: ${v.nota || "-"}</span><br>
        <span class="small">Foto: ${foto}</span><br>
        <span class="badge ${pendientes.length ? "badgeOrange" : "badgeGreen"}">Pendiente: ${pendientesTexto}</span>

        <hr>
        ${detalleHtml}

        ${(v.estado_vale==="abierto" || v.estado_vale==="parcial") ? `
          <hr>
          <div class="detalleVale">
            <b>Agregar herramienta a ${v.folio_sistema}</b>
            <p class="small">Úsalo cuando el trabajador vuelve a pedir más herramienta durante el día.</p>

            <div class="row3">
              <input id="addHerr_${v.id}" placeholder="Nueva herramienta / artículo">
              <input id="addCant_${v.id}" type="number" value="1" min="1" placeholder="Cantidad">
              <input id="addObs_${v.id}" placeholder="Observación">
            </div>

            <button class="green" onclick="agregarHerramientaVale(${v.id})">Agregar al vale</button>
          </div>
        ` : ""}

        <div class="btnRow">
          ${(v.estado_vale==="abierto" || v.estado_vale==="parcial") ? `
            <button class="orange" onclick="cerrarVale(${v.id})">Cerrar vale físico</button>
          ` : ""}

          ${(v.estado_vale==="cerrado" || v.estado_vale==="parcial") ? `
            <button class="gray" onclick="reabrirVale(${v.id})">Reabrir vale</button>
          ` : ""}

          ${(v.estado_vale!=="devuelto" && v.estado_vale!=="cancelado") ? `
            <button class="danger" onclick="cancelarVale(${v.id})">Cancelar vale</button>
          ` : ""}
        </div>

        <div class="row" style="margin-top:10px">
          <input id="arch_${v.id}" placeholder="Nueva ubicación física del papel">
          <button class="orange" onclick="moverArchivoFisico(${v.id})">Mover papel físico</button>
        </div>
      </div>
    `;
  }).join("");

  renderKpis();
}

/* =========================
   ACCIONES ADMIN
========================= */
async function crearUbicacion(){
  if(bloquearSiNoAdmin()) return;

  let nombre=document.getElementById("uNombre").value.trim();
  let tipo=document.getElementById("uTipo").value;
  let responsable=document.getElementById("uResp").value.trim();
  let empleado=document.getElementById("uEmpleado").value.trim();

  if(!nombre){
    alert("Pon nombre de ubicación");
    return;
  }

  let nueva={
    nombre:nombre,
    tipo:tipo,
    responsable:responsable || "Sin responsable",
    numero_empleado: empleado || "",
    organizacion_id:1
  };

  try{
    let res=await fetch(API+"/ubicaciones/ubicaciones/",{
      method:"POST",
      headers:headers(),
      body:JSON.stringify(nueva)
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo crear ubicación: " + error);
      return;
    }
  }catch(e){
    alert("Error de conexión creando ubicación");
    return;
  }

  let locales=getLocalUbicaciones();
  locales=unirPorNombre(locales,[nueva]);
  setLocalUbicaciones(locales);

  document.getElementById("uNombre").value="";
  document.getElementById("uResp").value="";
  document.getElementById("uEmpleado").value="";

  await cargarTodo();
  aplicarPermisos();

  alert("Ubicación creada y mostrada");
}

async function crearProducto(){
  if(bloquearSiNoAdmin()) return;

  let ubicacionSelect = document.getElementById("pUbicacion");

  if(!ubicacionSelect || !ubicacionSelect.value){
    alert("Selecciona una ubicación válida");
    return;
  }

  let ubicacionId = Number(ubicacionSelect.value);
  let ubicacionNombre = ubicacionSelect.options[ubicacionSelect.selectedIndex]?.dataset?.nombre || "";
  let cantidadInicial = Number(document.getElementById("pCant").value);

  let body = {
    nombre: document.getElementById("pNombre").value.trim(),
    codigo: document.getElementById("pCodigo").value.trim(),
    cantidad: 0,
    ubicacion: ubicacionNombre,
    tipo: document.getElementById("pTipo").value,
    precio: 0
  };

  if(!body.nombre || !body.codigo){
    alert("Falta nombre o código");
    return;
  }

  if(!cantidadInicial || cantidadInicial <= 0){
    alert("Cantidad inválida");
    return;
  }

  let creado = null;

  try{
    let res = await fetch(API + "/productos/productos/", {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(body)
    });

    if(!res.ok){
      let txt = await res.text();
      alert("Error creando producto: " + txt);
      return;
    }

    creado = await res.json();

  }catch(e){
    alert("Error de conexión creando producto");
    return;
  }

  try{
    let resEntrada = await fetch(API + "/movimientos/movimientos/", {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        producto_id: creado.id,
        ubicacion_id: ubicacionId,
        tipo: "entrada",
        cantidad: cantidadInicial,
        usuario: "frontend",
        recibe: "Alta de producto",
        empleado: "",
        nota: "Producto creado con stock inicial"
      })
    });

    if(!resEntrada.ok){
      let error = await resEntrada.text();
      alert("Producto creado, pero FALLÓ la entrada: " + error);
      await cargarTodo();
      aplicarPermisos();
      return;
    }

  }catch(e){
    alert("Producto creado, pero error en entrada");
    await cargarTodo();
    aplicarPermisos();
    return;
  }

  document.getElementById("pNombre").value = "";
  document.getElementById("pCodigo").value = "";
  document.getElementById("pCant").value = 1;

  await cargarTodo();
  aplicarPermisos();

  alert("Producto creado correctamente con stock real");
}

/* =========================
   ACCIONES USUARIO
========================= */
async function registrarSalida(){
  let valor=document.getElementById("sInventario").value;
  let cantidad=Number(document.getElementById("sCantidad").value);
  let recibe=document.getElementById("sRecibe").value.trim();
  let nota=document.getElementById("sNota").value.trim();

  if(!valor){
    alert("Selecciona producto con ubicación");
    return;
  }

  let partes=valor.split("|");
  let productoId=Number(partes[0]);
  let ubicacionId=Number(partes[1]);

  let inv=inventarioResumen.find(x=>
    String(x.producto_id)===String(productoId) &&
    String(x.ubicacion_id)===String(ubicacionId)
  );

  if(!inv){
    alert("No se encontró inventario real");
    return;
  }

  if(!cantidad || cantidad<=0){
    alert("Cantidad inválida");
    return;
  }

  if(cantidad > Number(inv.cantidad || 0)){
    alert("No hay suficiente stock en esa ubicación");
    return;
  }

  try{
    let res=await fetch(API+"/movimientos/movimientos/",{
      method:"POST",
      headers:headers(),
      body:JSON.stringify({
        producto_id:productoId,
        ubicacion_id:ubicacionId,
        tipo:"salida",
        cantidad:cantidad,
        recibe:recibe || "Sin nombre",
        empleado:"",
        nota:nota || "-",
        usuario:obtenerEmailUsuario() || "frontend"
      })
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo registrar salida: " + error);
      return;
    }
  }catch(e){
    alert("Error de conexión registrando salida");
    return;
  }

  document.getElementById("sCantidad").value=1;
  document.getElementById("sRecibe").value="";
  document.getElementById("sNota").value="";

  await cargarTodo();
  aplicarPermisos();

  alert("Salida registrada y descontada del inventario real");
}

async function registrarTraspaso(){
  let productoId=Number(document.getElementById("tProducto").value);
  let origenId=Number(document.getElementById("tOrigen").value);
  let destinoId=Number(document.getElementById("tDestino").value);
  let cantidad=Number(document.getElementById("tCantidad").value);
  let responsable=document.getElementById("tResponsable").value.trim();
  let nota=document.getElementById("tNota").value.trim();

  if(!productoId){
    alert("Selecciona producto");
    return;
  }

  if(!cantidad || cantidad<=0){
    alert("Cantidad inválida");
    return;
  }

  if(origenId===destinoId){
    alert("Origen y destino no pueden ser iguales");
    return;
  }

  try{
    let res=await fetch(API+"/traspasos/",{
      method:"POST",
      headers:headers(),
      body:JSON.stringify({
        producto_id:productoId,
        ubicacion_origen_id:origenId,
        ubicacion_destino_id:destinoId,
        cantidad:cantidad
      })
    });

    if(!res.ok){
      let error=await res.json();
      alert(error.detail || "No se pudo registrar traspaso");
      return;
    }
  }catch(e){
    alert("Error de conexión registrando traspaso");
    return;
  }

  let movimientosLocales=getLocalMovimientos();

  movimientosLocales.push({
    tipo:"traspaso",
    producto_id:productoId,
    producto_nombre:productosPantalla.find(p=>String(p.id)===String(productoId))?.nombre || "-",
    cantidad:cantidad,
    recibe:responsable || obtenerEmailUsuario() || "Movimiento interno",
    nota:nota || "Traspaso entre ubicaciones",
    ubicacion:`${nombreUbicacionPorId(origenId)} → ${nombreUbicacionPorId(destinoId)}`,
    fecha:new Date().toLocaleString()
  });

  setLocalMovimientos(movimientosLocales);

  document.getElementById("tCantidad").value=1;
  document.getElementById("tResponsable").value="";
  document.getElementById("tNota").value="";

  await cargarTodo();
  aplicarPermisos();

  alert("Traspaso registrado");
}

/* =========================
   VALES DE RESGUARDO
========================= */
function agregarRenglonVale(nombre="", cantidad=1, observacion=""){
  contadorRenglonesVale++;

  const contenedor=document.getElementById("contenedorDetallesVale");
  if(!contenedor) return;

  const id=contadorRenglonesVale;

  const div=document.createElement("div");
  div.className="detalleVale";
  div.id=`renglonVale_${id}`;

  div.innerHTML=`
    <div class="row3">
      <input id="vArt_${id}" placeholder="Herramienta / artículo" value="${nombre}">
      <input id="vCant_${id}" type="number" value="${cantidad}" min="1" placeholder="Cantidad">
      <input id="vObs_${id}" placeholder="Observación" value="${observacion}">
    </div>
    <button class="danger" type="button" onclick="eliminarRenglonVale(${id})">
      Quitar renglón
    </button>
  `;

  contenedor.appendChild(div);
}

function eliminarRenglonVale(id){
  const div=document.getElementById(`renglonVale_${id}`);
  if(div){
    div.remove();
  }
}

function obtenerDetallesValeFormulario(){
  let detalles=[];

  for(let i=1;i<=contadorRenglonesVale;i++){
    const art=document.getElementById(`vArt_${i}`);
    const cant=document.getElementById(`vCant_${i}`);
    const obs=document.getElementById(`vObs_${i}`);

    if(!art || !cant || !obs) continue;

    let nombre=art.value.trim();
    let cantidad=Number(cant.value);
    let observacion=obs.value.trim();

    if(nombre){
      detalles.push({
        herramienta_nombre:nombre,
        cantidad_entregada:cantidad > 0 ? cantidad : 1,
        observacion:observacion || null
      });
    }
  }

  return detalles;
}

function limpiarFormularioVale(){
  document.getElementById("vNumeroFisico").value="";
  document.getElementById("vFotoUrl").value="";
  document.getElementById("vEmpleado").value="";
  document.getElementById("vNumeroEmpleado").value="";
  document.getElementById("vPuesto").value="";
  document.getElementById("vArea").value="";
  document.getElementById("vUbicacionOrigen").value="";
  document.getElementById("vUbicacionFisica").value="Carpeta A / A0001-A0050";
  document.getElementById("vNota").value="";

  const contenedor=document.getElementById("contenedorDetallesVale");
  if(contenedor){
    contenedor.innerHTML="";
  }

  contadorRenglonesVale=0;
  agregarRenglonVale();
}

async function crearValeResguardo(){
  let detalles=obtenerDetallesValeFormulario();

  let body={
    numero_vale_fisico:document.getElementById("vNumeroFisico").value.trim() || null,
    empleado_recibe:document.getElementById("vEmpleado").value.trim(),
    numero_empleado:document.getElementById("vNumeroEmpleado").value.trim() || null,
    puesto:document.getElementById("vPuesto").value.trim() || null,
    area_frente:document.getElementById("vArea").value.trim() || null,
    ubicacion_origen:document.getElementById("vUbicacionOrigen").value.trim() || null,
    ubicacion_fisica_vale:document.getElementById("vUbicacionFisica").value.trim() || "Carpeta A",
    estado_archivo_fisico:"archivado",
    foto_url:document.getElementById("vFotoUrl").value.trim() || null,
    nota:document.getElementById("vNota").value.trim() || null,
    detalles:detalles
  };

  if(!body.empleado_recibe){
    alert("Falta empleado responsable");
    return;
  }

  if(detalles.length===0){
    alert("Agrega al menos una herramienta o artículo");
    return;
  }

  try{
    let res=await fetch(API+"/vales-resguardo/",{
      method:"POST",
      headers:headers(),
      body:JSON.stringify(body)
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo crear vale: " + error);
      return;
    }

    let data=await res.json();

    limpiarFormularioVale();
    await cargarValesAbiertos();
    await cargarTodo();

    alert("Vale creado: " + data.folio_sistema + ". Escríbelo en una esquina del vale físico.");

  }catch(e){
    alert("Error de conexión creando vale");
  }
}

async function cargarVales(renderizar=true){
  try{
    let res=await fetch(API+"/vales-resguardo/?t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(res.ok){
      valesPantalla=await res.json();
    }else{
      valesPantalla=[];
    }
  }catch(e){
    valesPantalla=[];
  }

  if(renderizar){
    renderVales();
    renderKpis();
  }
}

async function cargarValesAbiertos(renderizar=true){
  try{
    let res=await fetch(API+"/vales-resguardo/abiertos?t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(res.ok){
      valesPantalla=await res.json();
    }else{
      valesPantalla=[];
    }
  }catch(e){
    valesPantalla=[];
  }

  if(renderizar){
    renderVales();
    renderKpis();
  }
}

async function buscarVales(){
  let q=document.getElementById("buscarVale").value.trim();

  if(!q){
    await cargarValesAbiertos();
    return;
  }

  try{
    let res=await fetch(API+"/vales-resguardo/?q="+encodeURIComponent(q)+"&t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo buscar vales: " + error);
      return;
    }

    valesPantalla=await res.json();
    renderVales();
    renderKpis();

  }catch(e){
    alert("Error de conexión buscando vales");
  }
}

async function buscarReporteEmpleado(){
  let q=document.getElementById("buscarReporteEmpleado").value.trim();
  const div=document.getElementById("resultadoReporteEmpleado");

  if(!q){
    alert("Escribe nombre, número de empleado, folio o número de vale físico");
    return;
  }

  if(div){
    div.innerHTML=`<div class="liberacionBox liberacionSin">Buscando pendientes...</div>`;
  }

  try{
    let res=await fetch(API+"/vales-resguardo/reporte-empleado?q="+encodeURIComponent(q)+"&t="+Date.now(),{
      headers:headers(),
      cache:"no-store"
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo generar reporte: " + error);
      return;
    }

    let data=await res.json();
    renderReporteEmpleado(data);

  }catch(e){
    alert("Error de conexión generando reporte");
  }
}

function renderReporteEmpleado(data){
  const div=document.getElementById("resultadoReporteEmpleado");
  if(!div) return;

  if(!data.encontrado){
    div.innerHTML=`
      <div class="liberacionBox liberacionSin">
        <div class="tituloLiberacion">ℹ️ SIN REGISTROS</div>
        <p>${data.mensaje || "No se encontraron vales para esa búsqueda."}</p>
        <p class="small">Si el empleado ya tiene un vale físico, primero captúralo en el sistema.</p>
      </div>
    `;
    return;
  }

  let empleado=data.empleado || {};
  let clase=data.puede_salir ? "liberacionLibre" : "liberacionNo";
  let titulo=data.puede_salir ? "✅ LIBRE" : "⚠️ NO LIBERAR";

  let pendientesHtml="";

  if(data.vales_pendientes && data.vales_pendientes.length){
    pendientesHtml=data.vales_pendientes.map(v=>{
      let herramientas=(v.herramientas || []).map(h=>`
        <tr>
          <td>${h.herramienta_nombre || "-"}</td>
          <td>${h.item_code || "-"}</td>
          <td>${h.serie || "-"}</td>
          <td>${h.cantidad_entregada ?? 0}</td>
          <td>${h.cantidad_devuelta ?? 0}</td>
          <td><b>${h.cantidad_pendiente ?? 0}</b></td>
          <td>${h.estado || "-"}</td>
        </tr>
      `).join("");

      return `
        <div class="detalleVale">
          <b>Vale ${v.folio_sistema || "-"}</b> ${badgeEstadoVale(v.estado_vale)}<br>
          <span class="small">Vale físico: ${v.numero_vale_fisico || "-"} | Área: ${v.area_frente || "-"}</span><br>
          <span class="small">Papel físico: ${v.ubicacion_fisica_vale || "-"} | Responsable: ${v.responsable || "-"}</span>

          <table class="table" style="margin-top:8px">
            <thead>
              <tr>
                <th>Herramienta</th>
                <th>Código</th>
                <th>Serie</th>
                <th>Entregado</th>
                <th>Devuelto</th>
                <th>Pendiente</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>${herramientas}</tbody>
          </table>
        </div>
      `;
    }).join("");
  }else{
    pendientesHtml=`<p class="small">No hay herramientas pendientes por devolver.</p>`;
  }

  div.innerHTML=`
    <div class="liberacionBox ${clase}">
      <div class="tituloLiberacion">${titulo}</div>
      <p>${data.mensaje || "Reporte generado."}</p>

      <div class="row">
        <div>
          <span class="small">Empleado</span><br>
          <b>${empleado.empleado_recibe || "-"}</b>
        </div>
        <div>
          <span class="small">Número empleado</span><br>
          <b>${empleado.numero_empleado || "-"}</b>
        </div>
      </div>

      <div class="row">
        <div>
          <span class="small">Puesto</span><br>
          <b>${empleado.puesto || "-"}</b>
        </div>
        <div>
          <span class="small">Área / frente</span><br>
          <b>${empleado.area_frente || "-"}</b>
        </div>
      </div>

      <p>
        <span class="badge ${data.puede_salir ? "badgeGreen" : "badgeRed"}">
          Total pendiente: ${data.total_pendientes || 0}
        </span>
      </p>

      ${pendientesHtml}
    </div>
  `;
}

async function cerrarVale(valeId){
  if(!confirm("¿Cerrar este vale físico? Ya no se podrán agregar más herramientas hasta reabrirlo.")) return;

  try{
    let res=await fetch(API+`/vales-resguardo/${valeId}/cerrar`,{
      method:"POST",
      headers:headers()
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo cerrar vale: " + error);
      return;
    }

    await cargarValesAbiertos();
    alert("Vale cerrado. Si todavía debe herramienta, seguirá saliendo en reporte de bajas.");

  }catch(e){
    alert("Error de conexión cerrando vale");
  }
}

async function reabrirVale(valeId){
  if(!confirm("¿Reabrir este vale para agregar más herramientas?")) return;

  try{
    let res=await fetch(API+`/vales-resguardo/${valeId}/reabrir`,{
      method:"POST",
      headers:headers()
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo reabrir vale: " + error);
      return;
    }

    await cargarValesAbiertos();
    alert("Vale reabierto");

  }catch(e){
    alert("Error de conexión reabriendo vale");
  }
}

async function cancelarVale(valeId){
  if(!confirm("¿Cancelar este vale? Úsalo solo si fue una captura equivocada o el vale físico quedó anulado.")) return;

  try{
    let res=await fetch(API+`/vales-resguardo/${valeId}/cancelar`,{
      method:"POST",
      headers:headers()
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo cancelar vale: " + error);
      return;
    }

    await cargarValesAbiertos();
    alert("Vale cancelado");

  }catch(e){
    alert("Error de conexión cancelando vale");
  }
}

async function agregarHerramientaVale(valeId){
  let nombre=document.getElementById(`addHerr_${valeId}`).value.trim();
  let cantidad=Number(document.getElementById(`addCant_${valeId}`).value);
  let observacion=document.getElementById(`addObs_${valeId}`).value.trim();

  if(!nombre){
    alert("Escribe la herramienta o artículo");
    return;
  }

  if(!cantidad || cantidad<=0){
    alert("Cantidad inválida");
    return;
  }

  try{
    let res=await fetch(API+`/vales-resguardo/${valeId}/detalles`,{
      method:"POST",
      headers:headers(),
      body:JSON.stringify({
        herramienta_nombre:nombre,
        cantidad_entregada:cantidad,
        observacion:observacion || null
      })
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo agregar herramienta: " + error);
      return;
    }

    document.getElementById(`addHerr_${valeId}`).value="";
    document.getElementById(`addCant_${valeId}`).value=1;
    document.getElementById(`addObs_${valeId}`).value="";

    await cargarValesAbiertos();

    alert("Herramienta agregada al vale");

  }catch(e){
    alert("Error de conexión agregando herramienta al vale");
  }
}

async function registrarDevolucion(valeId,detalleId){
  let input=document.getElementById(`dev_${valeId}_${detalleId}`);
  let cantidad=Number(input?.value || 0);

  if(!cantidad || cantidad<=0){
    alert("Cantidad inválida para devolución");
    return;
  }

  let observacion=prompt("Observación de devolución:", "Entregó herramienta / artículo");

  try{
    let res=await fetch(API+`/vales-resguardo/${valeId}/devolver`,{
      method:"POST",
      headers:headers(),
      body:JSON.stringify({
        devoluciones:[
          {
            detalle_id:detalleId,
            cantidad_devuelta:cantidad,
            observacion:observacion || null
          }
        ]
      })
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo registrar devolución: " + error);
      return;
    }

    await cargarValesAbiertos();
    alert("Devolución registrada");

  }catch(e){
    alert("Error de conexión registrando devolución");
  }
}

async function moverArchivoFisico(valeId){
  let input=document.getElementById(`arch_${valeId}`);
  let nuevaUbicacion=input.value.trim();

  if(!nuevaUbicacion){
    alert("Escribe la nueva ubicación física del papel");
    return;
  }

  try{
    let res=await fetch(API+`/vales-resguardo/${valeId}/archivo-fisico`,{
      method:"PATCH",
      headers:headers(),
      body:JSON.stringify({
        ubicacion_fisica_vale:nuevaUbicacion,
        estado_archivo_fisico:"archivado"
      })
    });

    if(!res.ok){
      let error=await res.text();
      alert("No se pudo mover archivo físico: " + error);
      return;
    }

    await cargarValesAbiertos();
    alert("Ubicación física actualizada");

  }catch(e){
    alert("Error de conexión actualizando archivo físico");
  }
}

/* =========================
   RENGLÓN INICIAL
========================= */
document.addEventListener("DOMContentLoaded", ()=>{
  const contenedor=document.getElementById("contenedorDetallesVale");
  if(contenedor && contadorRenglonesVale===0){
    agregarRenglonVale();
  }
});

/* =========================
   SESIÓN GUARDADA
========================= */
if(tokenActual()){
  document.getElementById("login").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");

  aplicarPermisos();

  cargarTodo()
    .then(()=>aplicarPermisos())
    .catch((e)=>{
      console.error("Error cargando sesión guardada:", e);

      localStorage.removeItem("token");
      localStorage.removeItem("mexa_token");

      document.getElementById("app").classList.add("hidden");
      document.getElementById("login").classList.remove("hidden");

      document.getElementById("msg").innerText="Sesión vencida. Vuelve a entrar.";
    });
}
</script>

</body>
</html>
