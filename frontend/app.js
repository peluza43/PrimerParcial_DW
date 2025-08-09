const API_BASE = "http://127.0.0.1:5000";

const lista = document.querySelector("#listaRetos");
const modal = document.querySelector("#modal");
const btnAbrirModal = document.querySelector("#btnAbrirModal");
const btnCerrarModal = document.querySelector("#btnCerrarModal");
const btnCancelar = document.querySelector("#btnCancelar");
const form = document.querySelector("#formReto");

const filtroCategoria = document.querySelector("#filtroCategoria");
const filtroDificultad = document.querySelector("#filtroDificultad");
const btnFiltrar = document.querySelector("#btnFiltrar");
const btnLimpiar = document.querySelector("#btnLimpiar");

const cardTemplate = document.querySelector("#cardTemplate");

/* ---------- helpers UI ---------- */
function openModal(){ modal.classList.add("visible"); modal.classList.remove("hidden"); }
function closeModal(){ modal.classList.remove("visible"); setTimeout(()=>modal.classList.add("hidden"), 200); form.reset(); }

btnAbrirModal.addEventListener("click", openModal);
btnCerrarModal.addEventListener("click", closeModal);
btnCancelar.addEventListener("click", closeModal);

/* ---------- API ---------- */
async function apiGetRetos({ categoria="", dificultad="" } = {}){
  const params = new URLSearchParams();
  if (categoria) params.set("categoria", categoria);
  if (dificultad) params.set("dificultad", dificultad);
  const url = `${API_BASE}/retos${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Error al listar");
  return res.json();
}
async function apiCrearReto(body){
  const res = await fetch(`${API_BASE}/retos`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error("Error al crear reto");
  return res.json();
}
async function apiActualizarEstado(id, estado){
  const res = await fetch(`${API_BASE}/retos/${id}`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({estado})
  });
  if (!res.ok) throw new Error("Error al actualizar estado");
  return res.json();
}
async function apiEliminarReto(id){
  const res = await fetch(`${API_BASE}/retos/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Error al eliminar");
  return res.json();
}

/* ---------- render ---------- */
function renderRetos(retos){
  lista.innerHTML = "";
  if (!retos.length){
    lista.innerHTML = `<p style="opacity:.8">No hay retos con esos filtros.</p>`;
    return;
  }
  const frag = document.createDocumentFragment();
  for (const r of retos){
    const node = cardTemplate.content.cloneNode(true);
    node.querySelector(".card-title").textContent = r.titulo;
    node.querySelector(".card-desc").textContent = r.descripcion;
    node.querySelector(".categoria").textContent = r.categoria;
    node.querySelector(".dificultad").textContent = `dificultad: ${r.dificultad}`;
    const select = node.querySelector(".estadoSelect");
    select.value = r.estado;

    // acciones
    node.querySelector(".update").addEventListener("click", async () => {
      try{
        await apiActualizarEstado(r.id, select.value);
        toast("Estado actualizado");
      }catch(e){ alert(e.message); }
    });

    node.querySelector(".delete").addEventListener("click", async () => {
      if(!confirm("¿Eliminar este reto?")) return;
      try{
        await apiEliminarReto(r.id);
        await cargarRetos(); // refresca
      }catch(e){ alert(e.message); }
    });

    frag.appendChild(node);
  }
  lista.appendChild(frag);
}

/* ---------- events ---------- */
btnFiltrar.addEventListener("click", () => {
  cargarRetos({
    categoria: filtroCategoria.value,
    dificultad: filtroDificultad.value
  });
});
btnLimpiar.addEventListener("click", () => {
  filtroCategoria.value = "";
  filtroDificultad.value = "";
  cargarRetos();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    titulo: form.titulo.value.trim(),
    descripcion: form.descripcion.value.trim(),
    categoria: form.categoria.value.trim(),
    dificultad: form.dificultad.value,
    estado: form.estado.value
  };
  try{
    await apiCrearReto(data);
    closeModal();
    await cargarRetos();
    toast("Reto creado 🎉");
  }catch(e){
    alert(e.message);
  }
});

/* ---------- init ---------- */
async function cargarRetos(filters={}){
  try{
    const { retos } = await apiGetRetos(filters);
    renderRetos(retos);
  }catch(e){ alert(e.message); }
}
cargarRetos();

/* ---------- pequeño toast ---------- */
function toast(text){
  const el = document.createElement("div");
  el.textContent = text;
  Object.assign(el.style, {
    position:"fixed", bottom:"22px", left:"50%", transform:"translateX(-50%)",
    background:"#15183a", color:"#e9ecff", padding:"10px 14px", borderRadius:"10px",
    border:"1px solid #2a2f66", boxShadow:"0 10px 24px rgba(0,0,0,.35)", zIndex:9999,
    opacity:"0", transition:"opacity .2s ease"
  });
  document.body.appendChild(el);
  requestAnimationFrame(()=> el.style.opacity="1");
  setTimeout(()=>{ el.style.opacity="0"; setTimeout(()=>el.remove(), 220); }, 1500);
}
