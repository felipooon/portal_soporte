// Constantes oficiales del proyecto
const ENCARGADOS = {
  "Rodrigo Bustamante": ["Roger Vargas", "Bernardo Guenteo", "Freddy Blanco", "Orlando Andres Garate", "Alejandro Mansilla"],
  "Manuel Yovera": ["Armando Perez", "Cristian Norambuena", "Yerson Seron"],
  "Camilo Oyarzun": ["Mariluz Tocol", "Leonardo Valenzuela", "Luis Oyarzun", "Heriberto Lira"],
  "Francisco Vasquez": ["Carlos Rodriguez", "Carlos Salinas", "Eduin Campos", "Hayran Poveda", "Franco Quintallana", "Glenn Montiel", "Pablo Peréz"]
};

const EMPRESAS = [
  "Camanchaca", "AquaChile", "Mowi", "Cermaq", "Multiexport",
  "Abick", "Aquagen", "Salmones de Chile", "Blumar", "Ventisqueros",
  "Salmones Saysen", "Marine Farm", "Yadran", "Invermar", "Cooke",
  "Nova Austral", "Salmones Caleta Bay", "St-Andrews", "Salmones Magallanes",
  "Australis", "Aquasan", "Blu River", "Friosur", "Los Fiordos",
  "Salmones Austral", "Otro..."
];

const MAPA_ABREVIATURAS_EMPRESAS = {
  "st": { abbrev: "St", empresa: "St-Andrews" },
  "mw": { abbrev: "MW", empresa: "Mowi" },
  "sm": { abbrev: "SM", empresa: "Salmones Magallanes" },
  "au": { abbrev: "Au", empresa: "Australis" },
  "ca": { abbrev: "Ca", empresa: "Camanchaca" },
  "ce": { abbrev: "Ce", empresa: "Cermaq" },
  "mef": { abbrev: "Mef", empresa: "Multiexport" },
  "ab": { abbrev: "Ab", empresa: "Abick" },
  "ac": { abbrev: "AC", empresa: "AquaChile" },
  "as": { abbrev: "AS", empresa: "Aquasan" },
  "sc": { abbrev: "SC", empresa: "Salmones de Chile" },
  "bl": { abbrev: "Bl", empresa: "Blumar" },
  "ve": { abbrev: "VE", empresa: "Ventisqueros" },
  "br": { abbrev: "Br", empresa: "Blu River" },
  "sa": { abbrev: "SA", empresa: "Salmones Saysen" },
  "mf": { abbrev: "MF", empresa: "Marine Farm" },
  "fs": { abbrev: "FS", empresa: "Friosur" },
  "ya": { abbrev: "Ya", empresa: "Yadran" },
  "in": { abbrev: "In", empresa: "Invermar" },
  "ck": { abbrev: "Ck", empresa: "Cooke" },
  "na": { abbrev: "NA", empresa: "Nova Austral" },
  "lf": { abbrev: "LF", empresa: "Los Fiordos" },
  "sal": { abbrev: "SAL", empresa: "Salmones Austral" },
  "cb": { abbrev: "Cb", empresa: "Salmones Caleta Bay" }
};

function parseLocationInfo(loc) {
  if (!loc) return { empresa: null, nombre_centro: "" };
  const locClean = loc.trim().toLowerCase();
  if (!locClean) return { empresa: null, nombre_centro: "" };

  const parts = locClean.split("-");
  const prefix = parts[0];

  let rest = "";
  if (parts.length > 1) {
    rest = parts.slice(1).join("-");
  } else {
    rest = locClean;
  }

  // Insert space before numbers (e.g. tranqui1 -> tranqui 1)
  const restFormatted = rest.replace(/([a-zA-Z]+)(\d+)/g, "$1 $2");
  
  // Format in Title Case (Capitalize each word, no company prefix code)
  const nombre_centro = restFormatted
    .split(/[\s-]+/)
    .filter(w => w.length > 0)
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");

  let empresa = null;
  if (MAPA_ABREVIATURAS_EMPRESAS[prefix]) {
    empresa = MAPA_ABREVIATURAS_EMPRESAS[prefix].empresa;
  }

  return { empresa: empresa, nombre_centro: nombre_centro };
}
const TIPOS_EQUIPOS = [
  "Jennic simple", "Jennic doble", "Notebook", "Cámara", "Antena", "Estación Meteorológica", "Otro"
];

const TIPOS_SENSORES = [
  "Sensor Oxígeno - T°c", "Sensor Conductividad", "Sensor Oxígeno - Conductividad - T°c",
  "Sensor Sulfuro", "Sensor Redox", "Sensor pH", "Sensor Profundidad",
  "Sensor Nivel de Agua", "Sensor Salinidad", "Sensor Temperatura",
  "Sensor Corriente", "Sensor Turbidez", "Sensor Clorofila", "Sensor ADCP", "Otro"
];

const TIPOS_ELEMENTOS = TIPOS_EQUIPOS;

const RESPONSABLES_ACTIVACION = [
  "Hector Portillo",
  "Gabriel Moya",
  "Leonardo Araneda",
  "Felipe Godoy",
  "Edwin Gonzalez",
  "Ivan Soto",
  "Otro..."
];

// Estado global del certificado (Valores Oficiales Predeterminados)
let certificadoState = {
  datos_generales: {
    encargado_area: "Rodrigo Bustamante",
    empresa: "Camanchaca",
    location: "",
    nombre_centro: "",
    fecha_instalacion: new Date().toLocaleDateString('es-CL'),
    tecnico_visita: "Bernardo Guenteo",
    numero_ficha: "",
    coordenadas: "",
    barrio: "",
    puerto_patron: "",
    correo_centro: ""
  },
  infraestructura: {
    categoria: "Notebook",
    marca: "Lenovo",
    modelo: "Lenovo V14 G3 IAP",
    sistema_operativo: "Ubuntu 24.04 LTS",
    mac_ethernet: "",
    ip_vpn: ""
  },
  acceso_remoto: {
    protocolo: "OpenVPN",
    tun0: "10.9.18.37",
    hostserver: "dataweb.innovex.cl",
    puerto_server: "8888"
  },
  estacion_camara: {
    camara_instalada: "Si",
    modelo_camara: "Domo",
    conexion_camara: "Switch PoE",
    ip_fija_camara: "192.168.8.40",
    ubicacion_camara: "Pontón",
    estacion_instalada: "Si",
    modelo_estacion: "Davis",
    region_davis: "US",
    ubicacion_estacion: "Pontón",
    switch_poe: "Si",
    modelo_switch: "DS-3E0105P-E(B)",
    ubicacion_switch: "Pontón"
  },
  monitoreo_abiotico: {
    instalado: "Si",
    tipo_antena: "Outdoor",
    version: "v2.0.2",
    mac: "00:15:8D:00:09:24:53:F7",
    panid: "2020"
  },
  ubicacion_repuestos: "Bodega Pontón Principal",
  equipos_repuesto: [
    { tipo: "Equipo Jennic", mac: "00:15:8D:00:09:82:2A:A5", identificacion: "00:15:8D:00:09:82:2A:A5" },
    { tipo: "Sensor Integrado", metraje: "15", serie: "12345Y", identificacion: "12345Y" }
  ],
  ubicaciones: [
    {
      nombre: "Pontón Principal",
      coordenadas: "-42.749224 -73.580710",
      elementos: [
        { tipo: "Oxi-Sal", metraje: "5", serie: "12845" },
        { tipo: "Oxi-Sal", metraje: "10", serie: "12846" }
      ]
    }
  ],
  activacion: {
    ip_final: "10.170.47.28",
    interfaz: "wlp0s20f3",
    responsable_activacion: "Hector Portillo",
    estado_final: "Operativo"
  },
  evidencias: [],
  configuracion_alarmas: [],
  motes: [],
  observaciones: ""
};

// Inicialización cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  poblarDropdownsConstantes();
  bindFormInputs();
  poblarFormularioDesdeState();
  cargarListaCertificadosHeader(true);
  setupDragAndDrop();

  // Dark Mode Toggle
  const themeBtn = document.getElementById("btnToggleTheme");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      document.body.classList.toggle("dark-theme");
      const isDark = document.body.classList.contains("dark-theme");
      themeBtn.textContent = isDark ? "Modo Claro" : "Modo Oscuro";
    });
  }

  // Header Actions (Sin Popups)
  document.getElementById("btnHeaderNuevo").addEventListener("click", () => {
    crearNuevoCertificadoSinPopup();
  });

  document.getElementById("btnHeaderCargar").addEventListener("click", () => {
    const loc = document.getElementById("headerCertSelect").value;
    if (loc) cargarCertificadoPorLocation(loc);
    else mostrarToast("Seleccione un certificado de la lista del encabezado", "error");
  });

  const btnEliminar = document.getElementById("btnHeaderEliminar");
  if (btnEliminar) {
    btnEliminar.addEventListener("click", () => {
      const loc = document.getElementById("headerCertSelect").value || (certificadoState.datos_generales ? certificadoState.datos_generales.location : "");
      if (!loc) {
        mostrarToast("Seleccione un certificado de la lista del encabezado para eliminar", "warning");
        return;
      }
      if (confirm(`¿Está seguro que desea ELIMINAR permanentemente el certificado del centro '${loc}'? Esta acción borra el registro JSON, el PDF y sus imágenes asociadas.`)) {
        eliminarCertificadoPorLocation(loc);
      }
    });
  }

  document.getElementById("btnProcesarAutofill").addEventListener("click", procesarAutofill);
  document.getElementById("btnEjecutarSSHAutofill")?.addEventListener("click", ejecutarSSHAutofill);
  document.getElementById("btnCopiarComandoAutofill")?.addEventListener("click", copiarComandoPortapapeles);
  document.getElementById("btnGuardar").addEventListener("click", guardarAvance);
  document.getElementById("btnGenerarPDF").addEventListener("click", compilarYMostrarPDF);
  setupNavButtons();


  // Revisor & Verificación de Ingreso
  const btnEjecutarRevisor = document.getElementById("btnEjecutarRevisor");
  if (btnEjecutarRevisor) {
    btnEjecutarRevisor.addEventListener("click", ejecutarRevisorEquipos);
  }
  const btnCopiarPlantillaRevisor = document.getElementById("btnCopiarPlantillaRevisor");
  if (btnCopiarPlantillaRevisor) {
    btnCopiarPlantillaRevisor.addEventListener("click", copiarPlantillaRevisor);
  }
  const btnAutoRellenarDesdeRevisor = document.getElementById("btnAutoRellenarDesdeRevisor");
  if (btnAutoRellenarDesdeRevisor) {
    btnAutoRellenarDesdeRevisor.addEventListener("click", autoRellenarDesdeRevisor);
  }

  const inputsRevisor = [
    "rev_centro", "rev_host", "rev_usuario", "rev_tipo_conexion",
    "rev_sistema_operativo", "rev_kernel", "rev_clave_pc", "rev_dataweb",
    "rev_pcinnovex", "rev_cacheton", "rev_python3", "rev_weather_davis", "rev_visibility_cam",
    "rev_version_equipos", "rev_senal", "rev_voltajes",
    "rev_saturacion", "rev_salinidad", "rev_temperatura",
    "rev_camara", "rev_estacion", "rev_repuestos",
    "rev_repuesto_equipo", "rev_repuesto_sensor", "rev_repuesto_kit",
    "rev_telefono", "rev_correo", "rev_observaciones"
  ];
  inputsRevisor.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => construirPlantillaRevisorDesdeFormulario());
      el.addEventListener("change", () => construirPlantillaRevisorDesdeFormulario());
    }
  });

  // Información para ingreso de técnico
  const btnEjecutarIngresoTecnico = document.getElementById("btnEjecutarIngresoTecnico");
  if (btnEjecutarIngresoTecnico) {
    btnEjecutarIngresoTecnico.addEventListener("click", ejecutarIngresoTecnico);
  }
  const btnGenerarPlantillaIngreso = document.getElementById("btnGenerarPlantillaIngreso");
  if (btnGenerarPlantillaIngreso) {
    btnGenerarPlantillaIngreso.addEventListener("click", generarPlantillaIngreso);
  }
  const btnCopiarPlantillaIngreso = document.getElementById("btnCopiarPlantillaIngreso");
  if (btnCopiarPlantillaIngreso) {
    btnCopiarPlantillaIngreso.addEventListener("click", copiarPlantillaIngreso);
  }

  const inputsIngreso = [
    "ingreso_host", "ingreso_clave_pc", "ingreso_acceso_remoto",
    "ingreso_observaciones"
  ];
  inputsIngreso.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => generarPlantillaIngreso());
      el.addEventListener("change", () => generarPlantillaIngreso());
    }
  });

  const btnCopiarTextoPlanoHeader = document.getElementById("btnCopiarTextoPlanoHeader");
  if (btnCopiarTextoPlanoHeader) {
    btnCopiarTextoPlanoHeader.addEventListener("click", () => {
      if (moduloActivoActual === "revisor") {
        copiarPlantillaRevisor();
      } else if (moduloActivoActual === "ingreso_tecnico") {
        copiarPlantillaIngreso();
      }
    });
  }

  inicializarObservacionesGeneralesDefault();

  // Configurar Selector Principal de Módulos de Soporte
  setupModuleSwitcher();

  const btnSubtabPlantilla = document.getElementById("btnSubtabPlantilla");
  const btnSubtabDocumentoLive = document.getElementById("btnSubtabDocumentoLive");
  if (btnSubtabPlantilla && btnSubtabDocumentoLive) {
    btnSubtabPlantilla.addEventListener("click", () => {
      document.getElementById("viewPlantillaTexto").style.display = "block";
      document.getElementById("viewDocumentoLive").style.display = "none";
      btnSubtabPlantilla.classList.add("active");
      btnSubtabDocumentoLive.classList.remove("active");
    });
    btnSubtabDocumentoLive.addEventListener("click", () => {
      document.getElementById("viewPlantillaTexto").style.display = "none";
      document.getElementById("viewDocumentoLive").style.display = "block";
      btnSubtabDocumentoLive.classList.add("active");
      btnSubtabPlantilla.classList.remove("active");
      actualizarFrameDocumentoLive();
    });
  }

  const btnSubtabIngresoLive = document.getElementById("btnSubtabIngresoLive");
  const btnSubtabIngresoTexto = document.getElementById("btnSubtabIngresoTexto");
  if (btnSubtabIngresoLive && btnSubtabIngresoTexto) {
    btnSubtabIngresoLive.addEventListener("click", () => {
      document.getElementById("viewIngresoLive").style.display = "block";
      document.getElementById("viewIngresoTexto").style.display = "none";
      btnSubtabIngresoLive.classList.add("active");
      btnSubtabIngresoTexto.classList.remove("active");
      actualizarFrameDocumentoIngresoLive();
    });
    btnSubtabIngresoTexto.addEventListener("click", () => {
      document.getElementById("viewIngresoLive").style.display = "none";
      document.getElementById("viewIngresoTexto").style.display = "block";
      btnSubtabIngresoTexto.classList.add("active");
      btnSubtabIngresoLive.classList.remove("active");
    });
  }

  // Toggles de Vista Previa Derecha
  document.getElementById("btnToggleVistaHTML").addEventListener("click", () => {
    modoVistaPreviaModulos = "html";
    document.getElementById("liveHtmlContainer").style.display = "flex";
    document.getElementById("pdfContainer").style.display = "none";
    document.getElementById("btnToggleVistaHTML").classList.add("active");
    if (document.getElementById("btnToggleVistaPDF")) document.getElementById("btnToggleVistaPDF").classList.remove("active");
    if (document.getElementById("btnToggleVistaTexto")) document.getElementById("btnToggleVistaTexto").classList.remove("active");
    actualizarVistaPreviaDerechaPorModulo();
  });

  document.getElementById("btnToggleVistaPDF").addEventListener("click", () => {
    modoVistaPreviaModulos = "html";
    if (document.getElementById("btnToggleVistaTexto")) document.getElementById("btnToggleVistaTexto").classList.remove("active");
    compilarYMostrarPDF();
  });

  const btnToggleTexto = document.getElementById("btnToggleVistaTexto");
  if (btnToggleTexto) {
    btnToggleTexto.addEventListener("click", () => {
      mostrarTextoPlanoEnPanelDerecho();
    });
  }

  // Formulario Integrado Repuestos
  document.getElementById("btnToggleFormRepuesto").addEventListener("click", () => {
    const f = document.getElementById("formNuevoRepuesto");
    f.style.display = f.style.display === "none" ? "block" : "none";
  });
  document.getElementById("btnCancelarRepuesto").addEventListener("click", () => {
    document.getElementById("formNuevoRepuesto").style.display = "none";
  });
  document.getElementById("btnGuardarRepuesto").addEventListener("click", guardarNuevoRepuestoInline);

  document.getElementById("rep_tipo_select").addEventListener("change", (e) => {
    const esJennic = e.target.value === "Equipo Jennic";
    document.getElementById("group_rep_mac").style.display = esJennic ? "flex" : "none";
    document.getElementById("group_rep_serie").style.display = esJennic ? "none" : "flex";
    document.getElementById("group_rep_metraje").style.display = esJennic ? "none" : "flex";
  });

  // Formulario Ubicación
  document.getElementById("btnToggleFormUbicacion").addEventListener("click", () => {
    const f = document.getElementById("formNuevaUbicacion");
    f.style.display = f.style.display === "none" ? "block" : "none";
  });
  document.getElementById("btnCancelarUbicacion").addEventListener("click", () => {
    document.getElementById("formNuevaUbicacion").style.display = "none";
  });
  document.getElementById("btnGuardarUbicacion").addEventListener("click", guardarNuevaUbicacionInline);

  document.getElementById("btnAgregarFilaAlarma").addEventListener("click", agregarFilaAlarmaVacia);
  document.getElementById("btnProcesarPegadoAlarmas")?.addEventListener("click", procesarPegadoTextoAlarmas);

  document.getElementById("ub_repuestos_general").addEventListener("input", (e) => {
    certificadoState.ubicacion_repuestos = e.target.value;
    renderLiveHtmlSheet();
  });
});

// Crear nuevo certificado sin popup emergente
function crearNuevoCertificadoSinPopup() {
  certificadoState = {
    datos_generales: {
      location: "",
      nombre_centro: "",
      empresa: "Camanchaca",
      encargado_area: "Rodrigo Bustamante",
      tecnico_visita: "Bernardo Guenteo",
      fecha_instalacion: new Date().toLocaleDateString('es-CL'),
      numero_ficha: "",
      coordenadas: "",
      barrio: "",
      puerto_patron: "",
      correo_centro: ""
    },
    infraestructura: {
      categoria: "Notebook",
      marca: "Lenovo",
      modelo: "Lenovo V14 G3 IAP",
      sistema_operativo: "Ubuntu 24.04 LTS",
      mac_ethernet: "",
      ip_vpn: ""
    },
    acceso_remoto: {
      protocolo: "OpenVPN",
      tun0: "",
      hostserver: "dataweb.innovex.cl",
      puerto_server: "8888"
    },
    estacion_camara: {
      camara_instalada: "Si",
      modelo_camara: "Domo",
      conexion_camara: "Switch PoE",
      ip_fija_camara: "192.168.8.40",
      ubicacion_camara: "Pontón",
      estacion_instalada: "Si",
      modelo_estacion: "Davis",
      region_davis: "US",
      ubicacion_estacion: "Pontón",
      switch_poe: "Si",
      modelo_switch: "DS-3E0105P-E(B)",
      ubicacion_switch: "Pontón"
    },
    monitoreo_abiotico: {
      instalado: "Si",
      tipo_antena: "Outdoor",
      version: "v2.0.2",
      mac: "",
      panid: "2020"
    },
    ubicacion_repuestos: "",
    equipos_repuesto: [],
    ubicaciones: [],
    activacion: {
      ip_final: "",
      interfaz: "wlp0s20f3",
      responsable_activacion: "Hector Portillo",
      estado_final: "Operativo"
    },
    evidencias: [],
    configuracion_alarmas: [],
    motes: [],
    observaciones: ""
  };

  poblarFormularioDesdeState();
  
  const tabBtn = document.querySelector(".tab-btn[data-tab='generales']");
  if (tabBtn) tabBtn.click();
  
  const locInput = document.getElementById("gen_location");
  if (locInput) locInput.focus();

  mostrarToast("Nuevo certificado limpio iniciado. Complete Location ID y Nombre del Centro.", "info");
}

// Toast Notifications
function mostrarToast(mensaje, tipo = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.innerHTML = `<span>${mensaje}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3500);
}

// Poblar Dropdowns y resolver campos "Otro..."
function poblarDropdownsConstantes() {
  // Empresas
  const empSel = document.getElementById("gen_empresa_select");
  const empCustom = document.getElementById("gen_empresa_custom");
  empSel.innerHTML = "";
  EMPRESAS.forEach(emp => {
    const opt = document.createElement("option");
    opt.value = emp;
    opt.textContent = emp;
    empSel.appendChild(opt);
  });

  empSel.addEventListener("change", (e) => {
    if (e.target.value === "Otro...") {
      empCustom.style.display = "block";
      certificadoState.datos_generales.empresa = empCustom.value;
    } else {
      empCustom.style.display = "none";
      certificadoState.datos_generales.empresa = e.target.value;
    }
    renderLiveHtmlSheet();
  });

  empCustom.addEventListener("input", (e) => {
    certificadoState.datos_generales.empresa = e.target.value;
    renderLiveHtmlSheet();
  });

  // Encargados
  const encSel = document.getElementById("gen_encargado_select");
  encSel.innerHTML = "";
  Object.keys(ENCARGADOS).forEach(enc => {
    const opt = document.createElement("option");
    opt.value = enc;
    opt.textContent = enc;
    encSel.appendChild(opt);
  });

  encSel.addEventListener("change", (e) => {
    certificadoState.datos_generales.encargado_area = e.target.value;
    actualizarDropdownTecnicos(e.target.value);
    renderLiveHtmlSheet();
  });

  // Técnicos
  actualizarDropdownTecnicos("Rodrigo Bustamante");
  const tecCustom = document.getElementById("gen_tecnico_custom");
  document.getElementById("gen_tecnico_select").addEventListener("change", (e) => {
    if (e.target.value === "Otro...") {
      tecCustom.style.display = "block";
      certificadoState.datos_generales.tecnico_visita = tecCustom.value;
    } else {
      tecCustom.style.display = "none";
      certificadoState.datos_generales.tecnico_visita = e.target.value;
    }
    renderLiveHtmlSheet();
  });

  tecCustom.addEventListener("input", (e) => {
    certificadoState.datos_generales.tecnico_visita = e.target.value;
    renderLiveHtmlSheet();
  });

  // Responsables Activación
  const respSel = document.getElementById("act_responsable_select");
  const respCustom = document.getElementById("act_responsable_custom");
  respSel.innerHTML = "";
  RESPONSABLES_ACTIVACION.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r;
    opt.textContent = r;
    respSel.appendChild(opt);
  });

  respSel.addEventListener("change", (e) => {
    if (e.target.value === "Otro...") {
      respCustom.style.display = "block";
      certificadoState.activacion.responsable_activacion = respCustom.value;
    } else {
      respCustom.style.display = "none";
      certificadoState.activacion.responsable_activacion = e.target.value;
    }
    renderLiveHtmlSheet();
  });

  respCustom.addEventListener("input", (e) => {
    certificadoState.activacion.responsable_activacion = e.target.value;
    renderLiveHtmlSheet();
  });
}

function actualizarDropdownTecnicos(encargado) {
  const tecSel = document.getElementById("gen_tecnico_select");
  tecSel.innerHTML = "";

  const lista = ENCARGADOS[encargado] || [];
  lista.forEach(tec => {
    const opt = document.createElement("option");
    opt.value = tec;
    opt.textContent = tec;
    tecSel.appendChild(opt);
  });

  const optOtro = document.createElement("option");
  optOtro.value = "Otro...";
  optOtro.textContent = "Otro...";
  tecSel.appendChild(optOtro);

  if (lista.length > 0) {
    certificadoState.datos_generales.tecnico_visita = lista[0];
  }
}

let moduloActivoActual = "certificado"; // "certificado", "revisor", "ingreso_tecnico"

function activarSeccionTab(targetTab) {
  document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
  const targetId = `tab-${targetTab}`;
  const targetEl = document.getElementById(targetId);
  if (targetEl) {
    targetEl.classList.add("active");
  }

  // Sincronizar estado activo de los botones tab
  document.querySelectorAll(".tab-btn").forEach(t => {
    if (t.dataset.tab === targetTab) t.classList.add("active");
    else t.classList.remove("active");
  });

  // Re-renderizar listas al navegar para garantizar visualización inmediata
  try { renderMotesList(); } catch(e) {}
  try { renderUbicacionesList(); } catch(e) {}
  try { renderRepuestosList(); } catch(e) {}
  try { renderRepuestosMotesDropdown(); } catch(e) {}

  if (targetTab === "ingreso_tecnico") {
    prellenarDatosHostIngresoTecnico();
  }
  actualizarVistaPreviaDerechaPorModulo();
}

function setupModuleSwitcher() {
  const moduleBtns = document.querySelectorAll(".module-btn");
  moduleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      moduleBtns.forEach(b => {
        b.classList.remove("active");
        b.style.background = "var(--card-bg)";
        b.style.color = "var(--text-color)";
        b.style.borderColor = "var(--border-color)";
      });

      btn.classList.add("active");
      btn.style.background = "#0284c7";
      btn.style.color = "#ffffff";
      btn.style.borderColor = "#0284c7";

      const mod = btn.dataset.module;
      moduloActivoActual = mod;

      const navTabs = document.querySelector(".nav-tabs");
      const certGroup = document.getElementById("certSelectorGroup");
      const btnPDF = document.getElementById("btnGenerarPDF");
      const btnGuardar = document.getElementById("btnGuardar");
      const btnCopiarHeader = document.getElementById("btnCopiarTextoPlanoHeader");
      const btnToggleVistaPDF = document.getElementById("btnToggleVistaPDF");
      const btnToggleVistaTexto = document.getElementById("btnToggleVistaTexto");
      const btnToggleVistaHTML = document.getElementById("btnToggleVistaHTML");

      // Resetear toggles de vista previa al cambiar de módulo
      if (btnToggleVistaHTML) btnToggleVistaHTML.classList.add("active");
      if (btnToggleVistaPDF) btnToggleVistaPDF.classList.remove("active");
      if (btnToggleVistaTexto) btnToggleVistaTexto.classList.remove("active");
      const liveC = document.getElementById("liveHtmlContainer");
      const pdfC = document.getElementById("pdfContainer");
      if (liveC) liveC.style.display = "flex";
      if (pdfC) pdfC.style.display = "none";

      if (mod === "certificado") {
        if (navTabs) navTabs.style.display = "flex";
        if (certGroup) certGroup.style.display = "flex";
        if (btnPDF) btnPDF.style.display = "inline-block";
        if (btnGuardar) btnGuardar.style.display = "inline-block";
        if (btnCopiarHeader) btnCopiarHeader.style.display = "none";
        if (btnToggleVistaPDF) btnToggleVistaPDF.style.display = "inline-block";
        if (btnToggleVistaTexto) btnToggleVistaTexto.style.display = "none";

        activarSeccionTab("autofill");
      } else if (mod === "revisor") {
        if (navTabs) navTabs.style.display = "none";
        if (certGroup) certGroup.style.display = "none";
        if (btnPDF) btnPDF.style.display = "none";
        if (btnGuardar) btnGuardar.style.display = "none";
        if (btnCopiarHeader) btnCopiarHeader.style.display = "inline-block";
        if (btnToggleVistaPDF) btnToggleVistaPDF.style.display = "none";
        if (btnToggleVistaTexto) btnToggleVistaTexto.style.display = "inline-block";

        activarSeccionTab("revisor");
      } else if (mod === "ingreso_tecnico") {
        if (navTabs) navTabs.style.display = "none";
        if (certGroup) certGroup.style.display = "none";
        if (btnPDF) btnPDF.style.display = "none";
        if (btnGuardar) btnGuardar.style.display = "none";
        if (btnCopiarHeader) btnCopiarHeader.style.display = "inline-block";
        if (btnToggleVistaPDF) btnToggleVistaPDF.style.display = "none";
        if (btnToggleVistaTexto) btnToggleVistaTexto.style.display = "inline-block";

        activarSeccionTab("ingreso_tecnico");
      }
    });
  });
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const targetTab = tab.dataset.tab;
      const targetId = `tab-${targetTab}`;
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add("active");

      actualizarVistaPreviaDerechaPorModulo();

      if (targetTab === "ingreso_tecnico") {
        prellenarDatosHostIngresoTecnico();
      }
    });
  });
}

function actualizarVistaPreviaDerechaPorModulo() {
  const btnToggleTexto = document.getElementById("btnToggleVistaTexto");
  if (btnToggleTexto && btnToggleTexto.classList.contains("active")) {
    mostrarTextoPlanoEnPanelDerecho();
    return;
  }

  if (moduloActivoActual === "revisor") {
    mostrarVistaPreviaRevisorDerecha();
  } else if (moduloActivoActual === "ingreso_tecnico") {
    mostrarVistaPreviaIngresoDerecha();
  } else {
    restaurarVistaPreviaCertificadoDerecha();
  }
}

function restaurarVistaPreviaCertificadoDerecha() {
  // Asegurar que el contenedor HTML Live esté visible y el PDF oculto
  const liveContainer = document.getElementById("liveHtmlContainer");
  const pdfContainer = document.getElementById("pdfContainer");
  if (liveContainer) liveContainer.style.display = "flex";
  if (pdfContainer) pdfContainer.style.display = "none";

  // Asegurar el toggle activo correcto
  const btnHTML = document.getElementById("btnToggleVistaHTML");
  const btnPDF = document.getElementById("btnToggleVistaPDF");
  const btnTexto = document.getElementById("btnToggleVistaTexto");
  if (btnHTML) btnHTML.classList.add("active");
  if (btnPDF) btnPDF.classList.remove("active");
  if (btnTexto) btnTexto.classList.remove("active");

  // Renderizar el informe del certificado
  renderLiveHtmlSheet();
}

function bindFormInputs() {
  const mappings = [
    { id: "gen_location", sec: "datos_generales", key: "location" },
    { id: "gen_nombre_centro", sec: "datos_generales", key: "nombre_centro" },
    { id: "gen_numero_ficha", sec: "datos_generales", key: "numero_ficha" },
    { id: "gen_fecha_instalacion", sec: "datos_generales", key: "fecha_instalacion" },
    { id: "gen_coordenadas", sec: "datos_generales", key: "coordenadas" },
    { id: "gen_barrio", sec: "datos_generales", key: "barrio" },
    { id: "gen_puerto_patron", sec: "datos_generales", key: "puerto_patron" },
    { id: "gen_correo_centro", sec: "datos_generales", key: "correo_centro" },
    { id: "gen_area", sec: "datos_generales", key: "area" },
    { id: "gen_telefono_centro", sec: "datos_generales", key: "telefono_centro" },

    { id: "infra_area", sec: "infraestructura", key: "area" },
    { id: "infra_categoria", sec: "infraestructura", key: "categoria" },
    { id: "infra_marca", sec: "infraestructura", key: "marca" },
    { id: "infra_modelo", sec: "infraestructura", key: "modelo" },
    { id: "infra_so_select", sec: "infraestructura", key: "sistema_operativo" },
    { id: "infra_kernel", sec: "infraestructura", key: "kernel" },
    { id: "infra_mac_ethernet", sec: "infraestructura", key: "mac_ethernet" },
    { id: "infra_mac_wifi", sec: "infraestructura", key: "mac_wifi" },
    { id: "infra_pc_id", sec: "infraestructura", key: "pc_id" },
    { id: "infra_pc_password", sec: "infraestructura", key: "pc_password" },
    { id: "infra_tipo_ip", sec: "infraestructura", key: "tipo_ip" },
    { id: "infra_ip_fija", sec: "infraestructura", key: "ip_fija" },
    { id: "infra_ip_vpn", sec: "infraestructura", key: "ip_vpn" },

    { id: "acc_protocolo_select", sec: "acceso_remoto", key: "protocolo" },
    { id: "acc_tun0", sec: "acceso_remoto", key: "tun0" },
    { id: "acc_hostserver", sec: "acceso_remoto", key: "hostserver" },
    { id: "acc_puerto_server", sec: "acceso_remoto", key: "puerto_server" },

    { id: "cam_instalada", sec: "estacion_camara", key: "camara_instalada" },
    { id: "cam_modelo_camara", sec: "estacion_camara", key: "modelo_camara" },
    { id: "cam_mac_camara", sec: "estacion_camara", key: "mac_camara" },
    { id: "cam_conexion_camara", sec: "estacion_camara", key: "conexion_camara" },
    { id: "cam_ip_fija_camara", sec: "estacion_camara", key: "ip_fija_camara" },
    { id: "cam_ubicacion_camara", sec: "estacion_camara", key: "ubicacion_camara" },

    { id: "cam_estacion_instalada", sec: "estacion_camara", key: "estacion_instalada" },
    { id: "cam_modelo_estacion", sec: "estacion_camara", key: "modelo_estacion" },
    { id: "cam_id_estacion", sec: "estacion_camara", key: "id_estacion_meteorologica" },
    { id: "cam_altura_estacion", sec: "estacion_camara", key: "altura_estacion" },
    { id: "cam_region_davis", sec: "estacion_camara", key: "region_davis" },
    { id: "cam_ubicacion_estacion", sec: "estacion_camara", key: "ubicacion_estacion" },

    { id: "cam_switch_poe", sec: "estacion_camara", key: "switch_poe" },
    { id: "cam_modelo_switch", sec: "estacion_camara", key: "modelo_switch" },
    { id: "cam_ubicacion_switch", sec: "estacion_camara", key: "ubicacion_switch" },

    { id: "ab_instalado", sec: "monitoreo_abiotico", key: "instalado" },
    { id: "ab_tipo_antena", sec: "monitoreo_abiotico", key: "tipo_antena" },
    { id: "ab_ubicacion_antena", sec: "monitoreo_abiotico", key: "ubicacion_antena" },
    { id: "ab_version", sec: "monitoreo_abiotico", key: "version" },
    { id: "ab_mac", sec: "monitoreo_abiotico", key: "mac" },
    { id: "ab_panid", sec: "monitoreo_abiotico", key: "panid" },
    { id: "ab_cantidad_equipos_asociados", sec: "monitoreo_abiotico", key: "cantidad_equipos_asociados" },

    { id: "act_ip_final", sec: "activacion", key: "ip_final" },
    { id: "act_interfaz", sec: "activacion", key: "interfaz" },
    { id: "act_estado_final", sec: "activacion", key: "estado_final" },

    { id: "chk_pc_operativo", sec: "activacion_checklist", key: "pc_operativo" },
    { id: "chk_red_validada", sec: "activacion_checklist", key: "red_validada" },
    { id: "chk_antena_operativa", sec: "activacion_checklist", key: "antena_operativa" },
    { id: "chk_jennic_comunicando", sec: "activacion_checklist", key: "jennic_comunicando" },
    { id: "chk_sensores_datos", sec: "activacion_checklist", key: "sensores_datos" },
    { id: "chk_archivos_dat", sec: "activacion_checklist", key: "archivos_dat" },
    { id: "chk_transmision_estacion", sec: "activacion_checklist", key: "transmision_estacion" },
    { id: "chk_transmision_camara", sec: "activacion_checklist", key: "transmision_camara" },
    { id: "chk_datos_dataweb", sec: "activacion_checklist", key: "datos_dataweb" },
    { id: "chk_alarmas_estandar", sec: "activacion_checklist", key: "alarmas_estandar" }
  ];

  mappings.forEach(m => {
    const el = document.getElementById(m.id);
    if (el) {
      const handler = (e) => {
        const val = e.target.value;
        if (m.sec === "activacion_checklist") {
          if (!certificadoState.activacion) certificadoState.activacion = {};
          if (!certificadoState.activacion.checklist) certificadoState.activacion.checklist = {};
          certificadoState.activacion.checklist[m.key] = val;
        } else {
          if (!certificadoState[m.sec]) certificadoState[m.sec] = {};
          certificadoState[m.sec][m.key] = val;
        }

        if (m.id === "infra_tipo_ip") {
          actualizarVisibilidadConectividadIP();
        }

        // Auto-formateo especial para Location: Inferir Empresa y Nombre del Centro (Title Case sin código)
        if (m.id === "gen_location") {
          const parsed = parseLocationInfo(val);
          if (parsed.nombre_centro) {
            certificadoState.datos_generales.nombre_centro = parsed.nombre_centro;
            const elNom = document.getElementById("gen_nombre_centro");
            if (elNom) elNom.value = parsed.nombre_centro;
          }
          if (parsed.empresa) {
            certificadoState.datos_generales.empresa = parsed.empresa;
            const elEmp = document.getElementById("gen_empresa_select");
            if (elEmp) {
              elEmp.value = parsed.empresa;
              const cust = document.getElementById("gen_empresa_custom");
              if (cust) cust.style.display = "none";
            }
          }
        }

        renderLiveHtmlSheet();
      };
      el.addEventListener("input", handler);
      el.addEventListener("change", handler);
      el.addEventListener("blur", handler);
    }
  });

  const idsVisibilidad = ["cam_estacion_instalada", "cam_modelo_estacion", "cam_instalada", "cam_conexion_camara", "infra_tipo_ip", "ab_instalado"];
  idsVisibilidad.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", () => {
        actualizarVisibilidadCamaraEstacion();
        actualizarVisibilidadConectividadIP();
        // Toggle abiotic fields container
        if (id === "ab_instalado") {
          const containerAb = document.getElementById("abiotico_fields_container");
          if (containerAb) {
            containerAb.style.display = el.value === "No" ? "none" : "block";
          }
        }
        renderLiveHtmlSheet();
      });
    }
  });

  const obsEl = document.getElementById("obs_texto");
  if (obsEl) {
    const obsHandler = (e) => {
      certificadoState.observaciones = e.target.value;
      renderLiveHtmlSheet();
    };
    obsEl.addEventListener("input", obsHandler);
    obsEl.addEventListener("change", obsHandler);
  }
}

function actualizarVisibilidadCamaraEstacion() {
  const estInst = document.getElementById("cam_estacion_instalada")?.value;
  const modeloEst = document.getElementById("cam_modelo_estacion")?.value;
  const grpModeloEst = document.getElementById("group_modelo_estacion");
  const grpIdEst = document.getElementById("group_id_estacion");
  const grpAlturaEst = document.getElementById("group_altura_estacion");
  const grpRegionDavis = document.getElementById("group_region_davis");
  const grpUbicEst = document.getElementById("group_ubicacion_estacion");

  if (estInst === "Si") {
    if (grpModeloEst) grpModeloEst.style.display = "flex";
    if (grpIdEst) grpIdEst.style.display = "flex";
    if (grpAlturaEst) grpAlturaEst.style.display = "flex";
    if (grpUbicEst) grpUbicEst.style.display = "flex";
    if (modeloEst === "Davis") {
      if (grpRegionDavis) grpRegionDavis.style.display = "flex";
    } else {
      if (grpRegionDavis) grpRegionDavis.style.display = "none";
    }
  } else {
    if (grpModeloEst) grpModeloEst.style.display = "none";
    if (grpIdEst) grpIdEst.style.display = "none";
    if (grpAlturaEst) grpAlturaEst.style.display = "none";
    if (grpRegionDavis) grpRegionDavis.style.display = "none";
    if (grpUbicEst) grpUbicEst.style.display = "none";
  }

  const camInst = document.getElementById("cam_instalada")?.value;
  const conexionCam = document.getElementById("cam_conexion_camara")?.value;
  const grpModCam = document.getElementById("group_modelo_camara");
  const grpMacCam = document.getElementById("group_mac_camara");
  const grpConCam = document.getElementById("group_conexion_camara");
  const grpIpCam = document.getElementById("group_ip_camara");
  const grpUbicCam = document.getElementById("group_ubicacion_camara");
  const secSwitchPoe = document.getElementById("section_switch_poe");

  if (camInst === "Si") {
    if (grpModCam) grpModCam.style.display = "flex";
    if (grpMacCam) grpMacCam.style.display = "flex";
    if (grpConCam) grpConCam.style.display = "flex";
    if (grpIpCam) grpIpCam.style.display = "flex";
    if (grpUbicCam) grpUbicCam.style.display = "flex";

    if (conexionCam === "Switch PoE") {
      if (secSwitchPoe) secSwitchPoe.style.display = "block";
      if (!certificadoState.estacion_camara) certificadoState.estacion_camara = {};
      certificadoState.estacion_camara.switch_poe = "Si";
    } else {
      if (secSwitchPoe) secSwitchPoe.style.display = "none";
      if (!certificadoState.estacion_camara) certificadoState.estacion_camara = {};
      certificadoState.estacion_camara.switch_poe = "No";
    }
  } else {
    if (grpModCam) grpModCam.style.display = "none";
    if (grpMacCam) grpMacCam.style.display = "none";
    if (grpConCam) grpConCam.style.display = "none";
    if (grpIpCam) grpIpCam.style.display = "none";
    if (grpUbicCam) grpUbicCam.style.display = "none";
    if (secSwitchPoe) secSwitchPoe.style.display = "none";
    if (!certificadoState.estacion_camara) certificadoState.estacion_camara = {};
    certificadoState.estacion_camara.switch_poe = "No";
  }
}

function actualizarVisibilidadConectividadIP() {
  const tipoIp = document.getElementById("infra_tipo_ip") ? document.getElementById("infra_tipo_ip").value : "IP VPN tun0";
  const grpFija = document.getElementById("group_infra_ip_fija");
  const grpVpn = document.getElementById("group_infra_ip_vpn");

  if (grpFija) grpFija.style.display = (tipoIp === "IP Fija" || tipoIp === "Ambas") ? "block" : "none";
  if (grpVpn) grpVpn.style.display = (tipoIp === "IP VPN tun0" || tipoIp === "Ambas") ? "block" : "none";
}

function poblarFormularioDesdeState() {
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el && val !== undefined) el.value = val;
  };

  const dg = certificadoState.datos_generales || {};
  
  if (dg.location) {
    const parsed = parseLocationInfo(dg.location);
    if (parsed.nombre_centro && (!dg.nombre_centro || dg.nombre_centro === dg.location)) {
      dg.nombre_centro = parsed.nombre_centro;
    }
    if (parsed.empresa && !dg.empresa) {
      dg.empresa = parsed.empresa;
    }
  }

  setVal("gen_location", dg.location);
  setVal("gen_nombre_centro", dg.nombre_centro);
  setVal("gen_empresa_select", dg.empresa);
  setVal("gen_encargado_select", dg.encargado_area);
  setVal("gen_tecnico_select", dg.tecnico_visita);
  setVal("gen_numero_ficha", dg.numero_ficha);
  setVal("gen_fecha_instalacion", dg.fecha_instalacion);
  setVal("gen_coordenadas", dg.coordenadas);
  setVal("gen_barrio", dg.barrio);
  setVal("gen_puerto_patron", dg.puerto_patron);
  setVal("gen_correo_centro", dg.correo_centro);
  setVal("gen_area", dg.area || "");
  setVal("gen_telefono_centro", dg.telefono_centro || dg.numero_centro || "");

  const inf = certificadoState.infraestructura || {};
  setVal("infra_area", inf.area || "");
  setVal("infra_categoria", inf.categoria);
  setVal("infra_marca", inf.marca);
  setVal("infra_modelo", inf.modelo);
  setVal("infra_so_select", inf.sistema_operativo);
  setVal("infra_kernel", inf.kernel || "");
  setVal("infra_mac_ethernet", inf.mac_ethernet);
  setVal("infra_mac_wifi", inf.mac_wifi || "");
  setVal("infra_pc_id", inf.pc_id);
  setVal("infra_pc_password", inf.pc_password);
  setVal("infra_tipo_ip", inf.tipo_ip || "IP VPN tun0");
  setVal("infra_ip_fija", inf.ip_fija);
  setVal("infra_ip_vpn", inf.ip_vpn);
  actualizarVisibilidadConectividadIP();

  const acc = certificadoState.acceso_remoto || {};
  setVal("acc_protocolo_select", acc.protocolo);
  setVal("acc_tun0", acc.tun0);
  setVal("acc_hostserver", acc.hostserver);
  setVal("acc_puerto_server", acc.puerto_server);

  const cam = certificadoState.estacion_camara || {};
  setVal("cam_instalada", cam.camara_instalada || "No");
  setVal("cam_modelo_camara", cam.modelo_camara || "Domo");
  setVal("cam_mac_camara", cam.mac_camara || "");
  setVal("cam_conexion_camara", cam.conexion_camara || "Switch PoE");
  setVal("cam_ip_fija_camara", cam.ip_fija_camara || "");
  setVal("cam_ubicacion_camara", cam.ubicacion_camara || "Pontón");

  setVal("cam_estacion_instalada", cam.estacion_instalada || "No");
  setVal("cam_modelo_estacion", cam.modelo_estacion || "Davis");
  setVal("cam_id_estacion", cam.id_estacion_meteorologica || "");
  setVal("cam_altura_estacion", cam.altura_estacion || "");
  setVal("cam_region_davis", cam.region_davis || "US");
  setVal("cam_ubicacion_estacion", cam.ubicacion_estacion || "Pontón");

  setVal("cam_modelo_switch", cam.modelo_switch || "DS-3E0105P-E(B)");
  setVal("cam_ubicacion_switch", cam.ubicacion_switch || "Pontón");

  actualizarVisibilidadCamaraEstacion();

  const ab = certificadoState.monitoreo_abiotico || {};
  setVal("ab_instalado", ab.instalado);
  const containerAb = document.getElementById("abiotico_fields_container");
  if (containerAb) {
    containerAb.style.display = ab.instalado === "No" ? "none" : "block";
  }
  setVal("ab_tipo_antena", ab.tipo_antena);
  setVal("ab_ubicacion_antena", ab.ubicacion_antena || "Púlpito / Techo");
  setVal("ab_version", ab.version);
  setVal("ab_mac", ab.mac);
  setVal("ab_panid", ab.panid);
  setVal("ab_cantidad_equipos_asociados", ab.cantidad_equipos_asociados || "");

  const act = certificadoState.activacion || {};
  setVal("act_ip_final", act.ip_final);
  setVal("act_interfaz", act.interfaz);
  setVal("act_responsable_select", act.responsable_activacion || "Hector Portillo");
  setVal("act_estado_final", act.estado_final);

  const chk = act.checklist || {};
  setVal("chk_pc_operativo", chk.pc_operativo || "OK");
  setVal("chk_red_validada", chk.red_validada || "OK");
  setVal("chk_antena_operativa", chk.antena_operativa || "OK");
  setVal("chk_jennic_comunicando", chk.jennic_comunicando || "OK");
  setVal("chk_sensores_datos", chk.sensores_datos || "OK");
  setVal("chk_archivos_dat", chk.archivos_dat || "OK");
  setVal("chk_transmision_estacion", chk.transmision_estacion || "OK");
  setVal("chk_transmision_camara", chk.transmision_camara || "OK");
  setVal("chk_datos_dataweb", chk.datos_dataweb || "OK");
  setVal("chk_alarmas_estandar", chk.alarmas_estandar || "OK");

  setVal("ub_repuestos_general", certificadoState.ubicacion_repuestos || "");
  setVal("obs_texto", certificadoState.observaciones || "");

  try { renderMotesList(); } catch(e) {}
  try { renderRepuestosMotesDropdown(); } catch(e) {}
  try { renderUbicacionesList(); } catch(e) {}
  try { renderRepuestosList(); } catch(e) {}
  try { renderEvidenciasGrid(); } catch(e) {}
  try { renderAlarmasTabla(); } catch(e) {}
  try { renderLiveHtmlSheet(); } catch(e) {}
  try { actualizarVistaPreviaDerechaPorModulo(); } catch(e) {}
}

function setupDragAndDrop() {
  const dropEv = document.getElementById("dropzoneEvidencias");
  const fileEv = document.getElementById("fileEvidencias");

  if (dropEv && fileEv) {
    dropEv.addEventListener("click", () => fileEv.click());
    dropEv.addEventListener("dragover", (e) => { e.preventDefault(); dropEv.classList.add("dragover"); });
    dropEv.addEventListener("dragleave", () => dropEv.classList.remove("dragover"));
    dropEv.addEventListener("drop", (e) => {
      e.preventDefault();
      dropEv.classList.remove("dragover");
      if (e.dataTransfer.files.length) procesarArchivosEvidencias(e.dataTransfer.files);
    });
    fileEv.addEventListener("change", (e) => {
      if (e.target.files.length) procesarArchivosEvidencias(e.target.files);
    });
  }

  const dropAl = document.getElementById("dropzoneAlarmas");
  const fileAl = document.getElementById("fileAlarmas");

  if (dropAl && fileAl) {
    dropAl.addEventListener("click", () => fileAl.click());
    dropAl.addEventListener("dragover", (e) => { e.preventDefault(); dropAl.classList.add("dragover"); });
    dropAl.addEventListener("dragleave", () => dropAl.classList.remove("dragover"));
    dropAl.addEventListener("drop", (e) => {
      e.preventDefault();
      dropAl.classList.remove("dragover");
      if (e.dataTransfer.files.length) procesarArchivoAlarmas(e.dataTransfer.files[0]);
    });
    fileAl.addEventListener("change", (e) => {
      if (e.target.files.length) procesarArchivoAlarmas(e.target.files[0]);
    });
  }
}

async function procesarArchivosEvidencias(files) {
  const location = certificadoState.datos_generales.location || "ce-tranqui1";

  for (let file of files) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target.result;
      try {
        const res = await fetch("/api/upload_evidencia", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ nombre: file.name, base64: base64, location: location })
        });
        const data = await res.json();

        if (data.status === "ok") {
          if (!certificadoState.evidencias) certificadoState.evidencias = [];
          certificadoState.evidencias.push({ nombre: file.name, ruta: data.ruta, preview: base64 });
          renderEvidenciasGrid();
          renderLiveHtmlSheet();
          mostrarToast(`📷 Evidencia ${file.name} subida`, "success");
        }
      } catch (err) {
        mostrarToast("Error al subir evidencia: " + err.message, "error");
      }
    };
    reader.readAsDataURL(file);
  }
}

async function procesarArchivoAlarmas(file) {
  const location = certificadoState.datos_generales.location || "ce-tranqui1";
  const reader = new FileReader();

  reader.onload = async (e) => {
    const base64 = e.target.result;
    try {
      const res = await fetch("/api/upload_alarmas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: file.name, base64: base64, location: location })
      });
      const data = await res.json();

      if (data.status === "ok") {
        certificadoState.configuracion_alarmas = data.alarmas || [];
        renderAlarmasTabla();
        renderLiveHtmlSheet();
        mostrarToast(`📊 ${data.alarmas.length} alarmas importadas`, "success");
      }
    } catch (err) {
      mostrarToast("Error al procesar alarmas", "error");
    }
  };
  reader.readAsDataURL(file);
}

async function procesarPegadoTextoAlarmas() {
  const txt = document.getElementById("txtPegarAlarmas").value;
  if (!txt.trim()) {
    mostrarToast("Por favor pegue la tabla de alarmas en el recuadro", "warning");
    return;
  }

  try {
    const res = await fetch("/api/parse_alarmas_texto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: txt })
    });
    const data = await res.json();

    if (data.status === "ok" && data.alarmas && data.alarmas.length > 0) {
      if (!certificadoState.configuracion_alarmas) certificadoState.configuracion_alarmas = [];
      certificadoState.configuracion_alarmas.push(...data.alarmas);
      renderAlarmasTabla();
      renderLiveHtmlSheet();
      document.getElementById("txtPegarAlarmas").value = "";
      mostrarToast(`${data.alarmas.length} alarmas agregadas desde texto`, "success");
    } else {
      mostrarToast("No se detectaron filas válidas de alarmas en el texto pegado", "warning");
    }
  } catch (err) {
    mostrarToast("Error al procesar alarmas desde texto: " + err.message, "error");
  }
}

function renderEvidenciasGrid() {
  const container = document.getElementById("gridEvidencias");
  if (!container) return;

  container.innerHTML = "";
  const evs = certificadoState.evidencias || [];

  if (evs.length === 0) {
    container.innerHTML = `<div class="subtitle">Sin fotografías de evidencia subidas.</div>`;
    return;
  }

  evs.forEach((ev, idx) => {
    const card = document.createElement("div");
    card.className = "evidencia-card";
    card.style.position = "relative";
    const src = ev.preview || `/api/pdf_preview/2026/${certificadoState.datos_generales.location || 'ce-tranqui1'}/evidencias/${ev.nombre}`;
    const titulo = ev.titulo || ev.nombre || `Foto N° ${idx + 1}`;

    const btnSubir = idx > 0 ? `<button class="btn btn-small btn-secondary" onclick="subirEvidencia(${idx})" title="Mover Arriba">⬆️</button>` : '';
    const btnBajar = idx < evs.length - 1 ? `<button class="btn btn-small btn-secondary" onclick="bajarEvidencia(${idx})" title="Mover Abajo">⬇️</button>` : '';

    card.innerHTML = `
      <img src="${src}" alt="${titulo}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 6px 6px 0 0;">
      <div class="footer" style="padding: 8px; display: flex; flex-direction: column; gap: 6px; background: var(--card-bg);">
        <input type="text" value="${titulo}" onchange="actualizarNombreEvidencia(${idx}, this.value)" placeholder="Nombre o descripción foto..." style="font-size: 11px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; width: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 11px; font-weight: 600; color: var(--text-muted);">Foto N° ${idx + 1}</span>
          <div style="display: flex; gap: 4px;">
            ${btnSubir}
            ${btnBajar}
            <button class="btn btn-small btn-secondary" onclick="eliminarEvidencia(${idx})" title="Eliminar foto">❌</button>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function subirEvidencia(idx) {
  if (idx <= 0) return;
  const temp = certificadoState.evidencias[idx];
  certificadoState.evidencias[idx] = certificadoState.evidencias[idx - 1];
  certificadoState.evidencias[idx - 1] = temp;
  renderEvidenciasGrid();
  renderLiveHtmlSheet();
}

function bajarEvidencia(idx) {
  const evs = certificadoState.evidencias || [];
  if (idx >= evs.length - 1) return;
  const temp = certificadoState.evidencias[idx];
  certificadoState.evidencias[idx] = certificadoState.evidencias[idx + 1];
  certificadoState.evidencias[idx + 1] = temp;
  renderEvidenciasGrid();
  renderLiveHtmlSheet();
}

function actualizarNombreEvidencia(idx, nuevoNombre) {
  if (certificadoState.evidencias && certificadoState.evidencias[idx]) {
    certificadoState.evidencias[idx].titulo = nuevoNombre;
    certificadoState.evidencias[idx].nombre_mostrar = nuevoNombre;
    renderLiveHtmlSheet();
  }
}

function eliminarEvidencia(idx) {
  certificadoState.evidencias.splice(idx, 1);
  renderEvidenciasGrid();
  renderLiveHtmlSheet();
}

function normalizarAlarmaJS(al) {
  let status = al.status || 'Activo';
  let equipo = (al.equipo || '-').trim();
  let sensor = (al.sensor || '-').trim();
  let correo = al.correo || '-';
  let conf_min = al.conf_min || '-';
  let conf_max = al.conf_max || '-';
  let medicion = al.medicion || '-';
  let envio = al.envio || '60';

  const esSensorEnEquipo = (
    /^\(\d+\)/.test(equipo) ||
    equipo.toLowerCase().includes("sensor") ||
    equipo.includes(" - ") ||
    equipo.toLowerCase().includes("pontón") ||
    equipo.toLowerCase().includes("ponton") ||
    equipo.toLowerCase().includes("jaula")
  );

  if (esSensorEnEquipo) {
    const matchEq = equipo.match(/(Equipo\s*\d+)/i);
    const eqExtraido = matchEq ? matchEq[1] : "-";

    if (sensor === "-" || !sensor || sensor.toLowerCase() === "sin sensor") {
      sensor = equipo;
    }
    equipo = eqExtraido !== "-" ? eqExtraido : "Equipo 1";
  }

  if (/^\(\d+\)/.test(equipo) || equipo.includes(" - ")) {
    const matchEq = equipo.match(/(Equipo\s*\d+)/i);
    equipo = matchEq ? matchEq[1] : "Equipo 1";
  }

  let sensorClean = sensor.replace(/^\(\d+\)\s*/, '');
  if (sensorClean.includes(" - ")) {
    sensorClean = sensorClean.split(" - ")[0].trim();
  }

  if (!medicion || medicion === "-" || /^\(\d+\)/.test(medicion) || medicion.includes(" - ")) {
    const sLow = (sensor + " " + equipo + " " + sensorClean).toLowerCase();
    if (sLow.includes("oxygen") || sLow.includes("oxigeno") || sLow.includes("oxígeno") || sLow.includes("oxi")) {
      medicion = "Oxígeno";
    } else if (sLow.includes("salinity") || sLow.includes("salinidad")) {
      medicion = "Salinidad";
    } else if (sLow.includes("temperature") || sLow.includes("temperatura")) {
      medicion = "Temperatura";
    } else if (sLow.includes("orp")) {
      medicion = "ORP";
    } else if (sLow.includes("ph")) {
      medicion = "pH";
    } else if (sLow.includes("conductivid") || sLow.includes("conductivity")) {
      medicion = "Conductividad";
    } else {
      medicion = "Oxígeno";
    }
  }

  return {
    status: status,
    equipo: equipo,
    sensor: sensorClean || '-',
    correo: correo,
    conf_min: conf_min,
    conf_max: conf_max,
    medicion: medicion,
    envio: envio
  };
}

function renderAlarmasTabla() {
  const tbody = document.getElementById("tbodyAlarmas");
  if (!tbody) return;

  tbody.innerHTML = "";
  const alarmas = certificadoState.configuracion_alarmas || [];

  if (alarmas.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">Sin alarmas configuradas. Cargue un Excel o agregue una fila.</td></tr>`;
    return;
  }

  alarmas.forEach((alRaw, idx) => {
    const al = normalizarAlarmaJS(alRaw);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input type="text" value="${al.status}" onchange="actualizarAlarma(${idx}, 'status', this.value)"></td>
      <td><input type="text" value="${al.equipo}" onchange="actualizarAlarma(${idx}, 'equipo', this.value)"></td>
      <td><input type="text" value="${al.sensor}" onchange="actualizarAlarma(${idx}, 'sensor', this.value)"></td>
      <td><input type="text" value="${al.correo}" onchange="actualizarAlarma(${idx}, 'correo', this.value)"></td>
      <td><input type="text" value="${al.conf_min}" onchange="actualizarAlarma(${idx}, 'conf_min', this.value)"></td>
      <td><input type="text" value="${al.conf_max}" onchange="actualizarAlarma(${idx}, 'conf_max', this.value)"></td>
      <td><input type="text" value="${al.medicion}" onchange="actualizarAlarma(${idx}, 'medicion', this.value)"></td>
      <td><input type="text" value="${al.envio}" onchange="actualizarAlarma(${idx}, 'envio', this.value)"></td>
      <td><button class="btn btn-small btn-secondary" onclick="eliminarAlarma(${idx})" title="Eliminar alarma">❌</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function actualizarAlarma(idx, key, val) {
  if (!certificadoState.configuracion_alarmas) certificadoState.configuracion_alarmas = [];
  certificadoState.configuracion_alarmas[idx][key] = val;
  renderLiveHtmlSheet();
}

function agregarFilaAlarmaVacia() {
  if (!certificadoState.configuracion_alarmas) certificadoState.configuracion_alarmas = [];
  certificadoState.configuracion_alarmas.push({
    status: "Activada", equipo: "Equipo 1", sensor: "Sensor 5 mts Pontón", correo: "centro@camanchaca.cl",
    conf_min: "4,5", conf_max: "16,0", medicion: "Oxígeno", envio: "60"
  });
  renderAlarmasTabla();
  renderLiveHtmlSheet();
}

function eliminarAlarma(idx) {
  if (certificadoState.configuracion_alarmas) {
    certificadoState.configuracion_alarmas.splice(idx, 1);
    renderAlarmasTabla();
    renderLiveHtmlSheet();
  }
}

// RENDERIZADO INSTANTÁNEO A4 LIVE HTML 100% IDÉNTICO A REPORTLAB PDF
function renderLiveHtmlSheet() {
  try {
    const sheet = document.getElementById("liveHtmlSheet") || document.getElementById("reportlabSheet");
    if (!sheet) return;

    const dg = (certificadoState && certificadoState.datos_generales) || {};
    const inf = (certificadoState && certificadoState.infraestructura) || {};
    const acc = (certificadoState && certificadoState.acceso_remoto) || {};
    const cam = (certificadoState && certificadoState.estacion_camara) || {};
    const ab = (certificadoState && certificadoState.monitoreo_abiotico) || {};
    const act = (certificadoState && certificadoState.activacion) || {};
    const ubs = (certificadoState && certificadoState.ubicaciones) || [];
    const reps = (certificadoState && certificadoState.equipos_repuesto) || [];
    const als = (certificadoState && certificadoState.configuracion_alarmas) || [];
    const evs = (certificadoState && certificadoState.evidencias) || [];

    const fichaNo = dg.numero_ficha ? (dg.numero_ficha.startsWith("DS-") ? dg.numero_ficha : `DS-${dg.numero_ficha}`) : `DS-${(dg.location || "001").toUpperCase()}`;

    let htmlUbicacionesTables = "";
    if (!ubs || ubs.length === 0) {
      htmlUbicacionesTables = `<div style="font-size:10px; color:#666666; margin-bottom:8px;">Sin ubicaciones registradas.</div>`;
    } else {
      ubs.forEach(u => {
        if (!u) return;
        let rows = "";
        const elemList = u.elementos || u.equipos || [];
        if (!elemList || elemList.length === 0) {
          rows = `<tr><td colspan="4" style="text-align:center; color:#999999;">Sin equipos en esta ubicación.</td></tr>`;
        } else {
          elemList.forEach((el, idx) => {
            if (!el) return;
            const nombreEq = el.nombre || el.name || "";
            const tipoEq = el.tipo || "-";
            const labelEq = nombreEq ? `${nombreEq} (${tipoEq})` : tipoEq;
            const ident = el.mac ? `MAC: ${el.mac}` : (el.serie ? `S/N: ${el.serie}` : '-');

            let sensoresStr = "";
            if (el.sensores && el.sensores.length > 0) {
              const sensoresOrd = [...el.sensores].sort((a, b) => parseFloat(a.metros || 0) - parseFloat(b.metros || 0));
              sensoresStr = sensoresOrd.map(s => `• ${s.tipo_sensor || 'Sensor'} (${s.metros ? s.metros + 'm' : '-'})${s.sn ? ' [S/N: ' + s.sn + ']' : ''}`).join("<br>");
            } else if (el.metraje) {
              sensoresStr = `${el.metraje} metros`;
            } else {
              sensoresStr = "-";
            }

            rows += `<tr>
              <td style="text-align:center;">${idx + 1}</td>
              <td><strong>${labelEq}</strong></td>
              <td><code>${ident}</code></td>
              <td>${sensoresStr}</td>
            </tr>`;
          });
        }

        const coordsText = u.coordenadas ? ` <span style="font-weight:normal; color:#666666;">(GPS: ${u.coordenadas})</span>` : '';
        htmlUbicacionesTables += `
          <div style="font-size:10px; font-weight:bold; color:#333333; margin-top:6px; margin-bottom:3px;">
            Ubicación: ${u.nombre || 'Ubicación'}${coordsText}
          </div>
          <table class="reportlab-list-table">
            <thead>
              <tr>
                <th style="width:30px;">N°</th>
                <th>Equipo / Elemento</th>
                <th>MAC</th>
                <th>Sensores Asociados (Tipo — Metros)</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        `;
      });
    }

    let htmlRepuestosRows = "";
    if (reps && reps.length) {
      reps.forEach(r => {
        if (!r) return;
        const ident = r.mac ? `MAC: ${r.mac}` : (r.serie ? `S/N: ${r.serie}` : '-');
        htmlRepuestosRows += `<tr><td>${r.tipo || '-'}</td><td>${r.metraje ? r.metraje + 'm' : '-'}</td><td>${ident}</td></tr>`;
      });
    }

    let htmlAlarmasRows = "";
    if (als && als.length) {
      als.forEach(al => {
        if (!al) return;
        const norm = normalizarAlarmaJS(al);
        htmlAlarmasRows += `<tr>
          <td>${norm.status}</td>
          <td>${norm.equipo}</td>
          <td>${norm.sensor}</td>
          <td>${norm.correo}</td>
          <td>${norm.conf_min}</td>
          <td>${norm.conf_max}</td>
          <td>${norm.medicion}</td>
          <td>${norm.envio}</td>
        </tr>`;
      });
    }

    const chkData = act.checklist || {};
    const checklistItems = [
      { key: "pc_operativo", desc: "Computador instalado y operativo" },
      { key: "red_validada", desc: "Configuración de red validada" },
      { key: "antena_operativa", desc: "Antena receptora operativa" },
      { key: "jennic_comunicando", desc: "Todos los equipos Jennic comunicando" },
      { key: "sensores_datos", desc: "Sensores detectados y entregando datos" },
      { key: "archivos_dat", desc: "Archivos .dat generándose y guardándose" },
      { key: "transmision_estacion", desc: "Transmisión datos Estación Meteorológica" },
      { key: "transmision_camara", desc: "Transmisión datos Fotográficos" },
      { key: "datos_dataweb", desc: "Datos visibles y actualizando en DataWeb" },
      { key: "alarmas_estandar", desc: "Alarmas configuradas según estándar" }
    ];

    let htmlChecklistRows = "";
    checklistItems.forEach(ci => {
      const val = (chkData[ci.key] || "OK").toUpperCase();
      const isOk = val === "OK" || val === "SI" || val === "CONFORME";
      const isNA = val === "N/A" || val === "NO APLICA";
      const okMark = isOk ? "[ ✔ ]" : "[   ]";
      const naMark = isNA ? "[ ✔ ]" : "[   ]";
      const obs = isOk ? "Conforme" : (isNA ? "N/A" : "Pendiente");

      htmlChecklistRows += `<tr>
        <td>${ci.desc}</td>
        <td style="text-align:center;">${okMark}</td>
        <td style="text-align:center;">${naMark}</td>
        <td>${obs}</td>
      </tr>`;
    });

    const abioticoSeccionHtml = (ab.instalado !== 'No') ? `
      <tr><td class="attr">¿Monitoreo Abiótico?</td><td class="val">${ab.instalado || 'Si'}</td></tr>
      <tr><td class="attr">Tipo y Ubicación de Antena</td><td class="val">${ab.tipo_antena || 'Outdoor'} (${ab.ubicacion_antena || 'Púlpito / Techo'})</td></tr>
      <tr><td class="attr">Versión Firmware / MAC</td><td class="val">${ab.version || '-'} | MAC: ${ab.mac || '-'}</td></tr>
      <tr><td class="attr">Pan ID</td><td class="val">${ab.panid || '-'}</td></tr>
      ${ab.cantidad_equipos_asociados ? `<tr><td class="attr">Equipos Jennic Asociados</td><td class="val">${ab.cantidad_equipos_asociados}</td></tr>` : ''}
    ` : '';

    sheet.innerHTML = `
      <!-- Encabezado Oficial ReportLab 3 Cajas -->
      <div class="reportlab-header-box">
        <div class="reportlab-header-left">
          <img src="logo.png" alt="Innovex">
        </div>
        <div class="reportlab-header-center">
          VALIDACIÓN DE INSTALACIÓN
        </div>
        <div class="reportlab-header-right">
          <div class="row"><div class="lbl">N° Ficha</div><div class="val">${fichaNo}</div></div>
          <div class="row"><div class="lbl">Periodo</div><div class="val">2026</div></div>
          <div class="row"><div class="lbl">Páginas</div><div class="val">1 de 1</div></div>
        </div>
      </div>

      <!-- 1. Datos Generales -->
      <div class="reportlab-sec-title">1. Información general del centro</div>
      <table class="reportlab-attr-table">
        <tr><td class="attr">Location ID (Centro)</td><td class="val">${dg.location || '<em style="color:#ef4444;">[Sin asignar]</em>'}</td></tr>
        <tr><td class="attr">Nombre del Centro</td><td class="val">${dg.nombre_centro || '<em style="color:#ef4444;">[Sin asignar]</em>'}</td></tr>
        <tr><td class="attr">Empresa Cliente</td><td class="val">${dg.empresa || '-'}</td></tr>
        <tr><td class="attr">Encargado de Área</td><td class="val">${dg.encargado_area || '-'}</td></tr>
        <tr><td class="attr">Técnico de Visita</td><td class="val">${dg.tecnico_visita || '-'}</td></tr>
        <tr><td class="attr">Fecha de Instalación</td><td class="val">${dg.fecha_instalacion || '-'}</td></tr>
        <tr><td class="attr">Teléfono del Centro</td><td class="val">${dg.telefono_centro || dg.numero_centro || '-'}</td></tr>
        <tr><td class="attr">Correo del Centro</td><td class="val">${dg.correo_centro || '-'}</td></tr>
        <tr><td class="attr">Barrio / Zona</td><td class="val">${dg.barrio || '-'}</td></tr>
        <tr><td class="attr">Puerto Patrón</td><td class="val">${dg.puerto_patron || '-'}</td></tr>
        <tr><td class="attr">Coordenadas GPS</td><td class="val">${dg.coordenadas || '-'}</td></tr>
      </table>

      <!-- 2. Infraestructura & Conectividad -->
      <div class="reportlab-sec-title">2. Infraestructura del PC de Monitoreo & Conectividad</div>
      <table class="reportlab-attr-table">
        ${inf.area ? `<tr><td class="attr">Área</td><td class="val">${inf.area}</td></tr>` : ''}
        <tr><td class="attr">Categoría Equipo</td><td class="val">${inf.categoria || '-'}</td></tr>
        <tr><td class="attr">Marca / Modelo</td><td class="val">${inf.marca || ''} ${inf.modelo || ''}</td></tr>
        <tr><td class="attr">Sistema Operativo</td><td class="val">${inf.sistema_operativo || '-'}</td></tr>
        ${inf.kernel ? `<tr><td class="attr">Kernel</td><td class="val">${inf.kernel}</td></tr>` : ''}
        <tr><td class="attr">MAC Ethernet</td><td class="val">${inf.mac_ethernet || '-'}</td></tr>
        ${inf.mac_wifi ? `<tr><td class="attr">MAC Wi-Fi</td><td class="val">${inf.mac_wifi}</td></tr>` : ''}
        <tr><td class="attr">ID Equipo / PC</td><td class="val">${inf.pc_id || '-'}</td></tr>
        <tr><td class="attr">Contraseña PC</td><td class="val">${inf.pc_password || '-'}</td></tr>
        <tr><td class="attr">Tipo de Conexión IP</td><td class="val">${inf.tipo_ip || 'IP VPN tun0'}</td></tr>
        ${(inf.tipo_ip === 'IP Fija' || inf.tipo_ip === 'Ambas') ? `<tr><td class="attr">IP Fija PC</td><td class="val">${inf.ip_fija || '-'}</td></tr>` : ''}
        ${(inf.tipo_ip === 'IP VPN tun0' || inf.tipo_ip === 'Ambas' || !inf.tipo_ip) ? `<tr><td class="attr">IP VPN tun0</td><td class="val">${inf.ip_vpn || acc.tun0 || '-'}</td></tr>` : ''}
        <tr><td class="attr">Protocolo VPN</td><td class="val">${acc.protocolo || '-'}</td></tr>
        <tr><td class="attr">Servidor Host / Puerto</td><td class="val">${acc.hostserver || 'dataweb.innovex.cl'}:${acc.puerto_server || '8888'}</td></tr>
      </table>

      <!-- 3. Antena, Cámara & Estación Meteorológica -->
      <div class="reportlab-sec-title">3. Antena, Estación Meteorológica & Cámara</div>
      <table class="reportlab-attr-table">
        ${abioticoSeccionHtml}
        <tr>
          <td class="attr">Estación Meteorológica</td>
          <td class="val">${cam.estacion_instalada === 'Si' ? `${cam.modelo_estacion || 'Davis'} ${cam.id_estacion_meteorologica ? `[ID: ${cam.id_estacion_meteorologica}]` : ''} ${cam.altura_estacion ? `[Altura: ${cam.altura_estacion}m]` : ''} ${cam.modelo_estacion === 'Davis' && cam.region_davis ? `(Región ${cam.region_davis})` : ''} - Ubicación: ${cam.ubicacion_estacion || 'Pontón'}` : 'No'}</td>
        </tr>
        <tr>
          <td class="attr">Cámara de Alimentación</td>
          <td class="val">${cam.camara_instalada === 'Si' ? `${cam.modelo_camara || 'Domo'} ${cam.mac_camara ? `[MAC: ${cam.mac_camara}]` : ''} (${cam.conexion_camara || 'Switch PoE'}) - IP: ${cam.ip_fija_camara || '-'} - Ubicación: ${cam.ubicacion_camara || 'Pontón'}` : 'No'}</td>
        </tr>
        <tr>
          <td class="attr">Switch PoE</td>
          <td class="val">${cam.switch_poe === 'Si' && cam.conexion_camara === 'Switch PoE' ? `${cam.modelo_switch || 'DS-3E0105P-E(B)'} - Ubicación: ${cam.ubicacion_switch || 'Pontón'}` : 'No'}</td>
        </tr>
      </table>

      ${ab.instalado !== 'No' ? `
        <!-- 4. Ubicaciones e Instalación -->
        <div class="reportlab-sec-title">4. Detalle de equipos instalados por ubicación</div>
        ${htmlUbicacionesTables}

        <!-- 5. Repuestos -->
        <div class="reportlab-sec-title">5. Equipos de repuesto (Almacenamiento: ${certificadoState.ubicacion_repuestos || 'Bodega Pontón'})</div>
        ${(reps && reps.length) ? `
          <table class="reportlab-list-table">
            <thead><tr><th>Tipo de Equipo</th><th>Metros</th><th>MAC</th></tr></thead>
            <tbody>${htmlRepuestosRows}</tbody>
          </table>
        ` : '<div style="font-size:10px; color:#666666; margin-bottom:8px;">Sin repuestos registrados.</div>'}
      ` : ''}

      <!-- Activación -->
      <div class="reportlab-sec-title">${ab.instalado !== 'No' ? '6' : '4'}. Validación de activación del servicio</div>
      <table class="reportlab-attr-table">
        <tr><td class="attr">IP Asignada / Interfaz</td><td class="val">${act.ip_final || '-'} (${act.interfaz || '-'})</td></tr>
        <tr><td class="attr">Responsable Activación</td><td class="val">${act.responsable_activacion || '-'}</td></tr>
        <tr><td class="attr">Estado Final</td><td class="val"><strong>${act.estado_final || 'Operativo'}</strong></td></tr>
      </table>
      <div style="font-weight:bold; font-size:10px; margin-top:6px; margin-bottom:3px; color:#222222;">Checklist de Validación de Operatividad:</div>
      <table class="reportlab-list-table">
        <thead><tr><th>Validación</th><th style="text-align:center;">OK</th><th style="text-align:center;">N/A</th><th>Observación</th></tr></thead>
        <tbody>${htmlChecklistRows}</tbody>
      </table>

      <!-- Alarmas -->
      ${(als && als.length) ? `
        <div class="reportlab-sec-title">${ab.instalado !== 'No' ? '7' : '5'}. Configuración de alarmas</div>
        <table class="reportlab-list-table">
          <thead><tr><th>Status</th><th>Equipo</th><th>Sensor</th><th>Usuario</th><th>Mín</th><th>Máx</th><th>Medición</th><th>Envío</th></tr></thead>
          <tbody>${htmlAlarmasRows}</tbody>
        </table>
      ` : ''}

      <!-- Observaciones -->
      <div class="reportlab-sec-title">${ab.instalado !== 'No' ? (als && als.length ? '8' : '7') : (als && als.length ? '6' : '5')}. Observaciones y notas libres</div>
      <div class="reportlab-obs-box">
        ${certificadoState.observaciones || '<span style="color:#aaaaaa;">[ Espacio reservado para notas de campo y firma del cliente ]</span>'}
      </div>

      <!-- Registro Fotográfico -->
      ${(evs && evs.length) ? `
        <div class="reportlab-sec-title">${ab.instalado !== 'No' ? (als && als.length ? '9' : '8') : (als && als.length ? '7' : '6')}. Registro fotográfico</div>
        <div style="font-size:10px; color:#555555; margin-bottom:8px;">Adjuntas ${evs.length} fotografía(s) de evidencia técnica.</div>
      ` : ''}
    `;
  } catch (err) {
    console.error("Error en renderLiveHtmlSheet:", err);
  }
}

let sensoresDraft = {};

function agregarSensorDraft(ubIdx) {
  const tipoSensor = document.getElementById(`elem_sensor_tipo_${ubIdx}`).value;
  const metros = document.getElementById(`elem_sensor_metros_${ubIdx}`).value.trim();
  const snInput = document.getElementById(`elem_sensor_sn_${ubIdx}`);
  const sn = snInput ? snInput.value.trim() : "";
  if (!sensoresDraft[ubIdx]) sensoresDraft[ubIdx] = [];
  sensoresDraft[ubIdx].push({ tipo_sensor: tipoSensor, metros: metros, sn: sn });
  if (snInput) snInput.value = "";
  const mInput = document.getElementById(`elem_sensor_metros_${ubIdx}`);
  if (mInput) mInput.value = "";
  renderSensoresDraft(ubIdx);
}

function eliminarSensorDraft(ubIdx, sIdx) {
  if (sensoresDraft[ubIdx]) {
    sensoresDraft[ubIdx].splice(sIdx, 1);
    renderSensoresDraft(ubIdx);
  }
}

function renderSensoresDraft(ubIdx) {
  const container = document.getElementById(`lista_sensores_draft_${ubIdx}`);
  if (!container) return;
  const list = sensoresDraft[ubIdx] || [];
  if (list.length === 0) {
    container.innerHTML = `<span style="font-size: 11px; color: var(--text-muted);">Sin sensores asociados.</span>`;
    return;
  }
  container.innerHTML = list.map((s, idx) => `
    <span class="badge badge-info" style="margin:2px; display:inline-flex; align-items:center; gap:4px;">
      ${s.tipo_sensor} (${s.metros ? s.metros + 'm' : '-'})${s.sn ? ' [S/N: ' + s.sn + ']' : ''}
      <button type="button" onclick="eliminarSensorDraft(${ubIdx}, ${idx})" style="border:none; background:transparent; color:red; cursor:pointer; font-weight:bold;">×</button>
    </span>
  `).join(" ");
}

function renderUbicacionesList() {
  const container = document.getElementById("contenedorUbicaciones");
  if (!container) return;

  container.innerHTML = "";
  const ubicaciones = certificadoState.ubicaciones || [];

  if (ubicaciones.length === 0) {
    container.innerHTML = `<div class="subtitle">No hay ubicaciones registradas.</div>`;
    return;
  }

  ubicaciones.forEach((ub, ubIdx) => {
    const card = document.createElement("div");
    card.className = "ubicacion-card";
    const coordsStr = ub.coordenadas ? ` (${ub.coordenadas})` : "";
    const elementos = ub.elementos || [];

    let elementosRows = "";
    elementos.forEach((elem, elIdx) => {
      const nombreEq = elem.nombre || elem.name || "";
      const tipoEq = elem.tipo || "-";
      const labelEq = nombreEq ? `<strong>${nombreEq}</strong> (${tipoEq})` : `<strong>${tipoEq}</strong>`;
      const serieStr = elem.serie || elem.mac || "-";
      
      let sensoresHtml = "";
      if (elem.sensores && elem.sensores.length > 0) {
        const sensoresOrd = [...elem.sensores].sort((a, b) => parseFloat(a.metros || 0) - parseFloat(b.metros || 0));
        sensoresHtml = sensoresOrd.map(s => {
          const snStr = s.sn ? ` [S/N: ${s.sn}]` : '';
          return `<span class="badge badge-info" style="margin:2px;">${s.tipo_sensor} (${s.metros ? s.metros + 'm' : '-'})${snStr}</span>`;
        }).join(" ");
      } else if (elem.metraje) {
        sensoresHtml = `<span class="badge badge-secondary">${elem.metraje}m</span>`;
      } else {
        sensoresHtml = `<span style="color:#aaa;">Sin sensores</span>`;
      }

      elementosRows += `
        <tr>
          <td>${labelEq}</td>
          <td><code>${serieStr}</code></td>
          <td>${sensoresHtml}</td>
          <td style="width: 40px; text-align: center;">
            <button class="btn btn-small btn-secondary" onclick="eliminarElementoUbicacion(${ubIdx}, ${elIdx})" title="Eliminar equipo">❌</button>
          </td>
        </tr>
      `;
    });

    const motesList = certificadoState.motes || [];
    const motesOrdenados = [...motesList].sort((a, b) => {
      const nameA = a.asociacion || a.name || "";
      const nameB = b.asociacion || b.name || "";
      return nameA.localeCompare(nameB, undefined, { numeric: true, sensitivity: 'base' });
    });

    let motesOptionsHtml = `<option value="">-- Seleccionar Mote detectado (${motesList.length} detectados) --</option>`;
    motesOrdenados.forEach(m => {
      const name = m.asociacion || m.name || `Equipo ${m.mote || ''}`;
      motesOptionsHtml += `<option value="${m.mac}" data-name="${name}">${name} (MAC: ${m.mac})</option>`;
    });

    const motesDropdownElemHtml = motesList.length > 0 ? `
      <div class="form-group" style="grid-column: span 3;">
        <label style="color: var(--primary-color, #2563eb);">Asignar MAC y Nombre de Mote Detectado</label>
        <select id="select_mote_elem_${ubIdx}" onchange="
          if(this.value){ 
            document.getElementById('elem_serie_${ubIdx}').value = this.value; 
            const selectedOpt = this.options[this.selectedIndex];
            if(selectedOpt && selectedOpt.dataset.name) {
              document.getElementById('elem_nombre_${ubIdx}').value = selectedOpt.dataset.name;
            }
          }">
          ${motesOptionsHtml}
        </select>
      </div>
    ` : '';

    card.innerHTML = `
      <div class="ubicacion-header">
        <div>
          <h3>${ub.nombre} <span style="font-size:12px; color:var(--text-muted);">${coordsStr}</span></h3>
        </div>
        <div>
          <button class="btn btn-small btn-primary" onclick="mostrarFormNuevoElemento(${ubIdx})">➕ Elemento</button>
          <button class="btn btn-small btn-secondary" onclick="eliminarUbicacion(${ubIdx})">❌ Eliminar</button>
        </div>
      </div>

      <div id="formNuevoElem_${ubIdx}" class="inline-form-card" style="display: none;">
        <h3>Agregar Equipo Instalado en ${ub.nombre}</h3>
        <div class="form-grid">
          ${motesDropdownElemHtml}
          <div class="form-group">
            <label>Tipo Equipo</label>
            <select id="elem_tipo_${ubIdx}">
              ${TIPOS_EQUIPOS.map(t => `<option value="${t}">${t}</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label>Nombre / Identificador Equipo</label>
            <input type="text" id="elem_nombre_${ubIdx}" placeholder="ej. Name 1 / Mote 01">
          </div>
          <div class="form-group">
            <label>MAC</label>
            <input type="text" id="elem_serie_${ubIdx}" placeholder="ej. 00:15:8D:00:09:24:53:F7">
          </div>
        </div>

        <div style="margin-top: 12px; padding: 10px; background: var(--bg-color, #f8fafc); border-radius: 6px; border: 1px solid var(--border-color, #e2e8f0);">
          <h4 style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">Sensores Asociados a este Equipo</h4>
          <div class="form-grid">
            <div class="form-group">
              <label>Tipo Sensor</label>
              <select id="elem_sensor_tipo_${ubIdx}">
                ${TIPOS_SENSORES.map(s => `<option value="${s}">${s}</option>`).join("")}
              </select>
            </div>
            <div class="form-group">
              <label>Metros (m)</label>
              <input type="text" id="elem_sensor_metros_${ubIdx}" placeholder="ej. 5">
            </div>
            <div class="form-group">
              <label>S/N Sensor (Opcional)</label>
              <input type="text" id="elem_sensor_sn_${ubIdx}" placeholder="ej. SN-98765">
            </div>
            <div class="form-group" style="display: flex; align-items: flex-end;">
              <button type="button" class="btn btn-small btn-secondary" onclick="agregarSensorDraft(${ubIdx})">➕ Agregar Sensor</button>
            </div>
          </div>
          <div id="lista_sensores_draft_${ubIdx}" style="margin-top: 6px;"></div>
        </div>

        <div class="form-buttons" style="margin-top: 12px;">
          <button class="btn btn-primary btn-small" onclick="guardarElementoUbicacion(${ubIdx})">Guardar Equipo</button>
          <button class="btn btn-secondary btn-small" onclick="ocultarFormNuevoElemento(${ubIdx})">Cancelar</button>
        </div>
      </div>

      ${elementos.length > 0 ? `
        <table class="elementos-table">
          <thead><tr><th>Equipo / Elemento</th><th>MAC</th><th>Sensores Asociados (Tipo — Metros)</th><th>Acción</th></tr></thead>
          <tbody>${elementosRows}</tbody>
        </table>
      ` : `<div class="subtitle" style="margin-top:8px;">Sin equipos instalados.</div>`}
    `;

    container.appendChild(card);
  });
}

function guardarNuevaUbicacionInline() {
  const nombre = document.getElementById("nueva_ub_nombre").value.trim();
  const coords = document.getElementById("nueva_ub_coords").value.trim();
  if (!nombre) return;

  if (!certificadoState.ubicaciones) certificadoState.ubicaciones = [];
  certificadoState.ubicaciones.push({ nombre: nombre, coordenadas: coords, elementos: [] });

  document.getElementById("nueva_ub_nombre").value = "";
  document.getElementById("nueva_ub_coords").value = "";
  document.getElementById("formNuevaUbicacion").style.display = "none";

  renderUbicacionesList();
  renderLiveHtmlSheet();
}

function eliminarUbicacion(idx) {
  certificadoState.ubicaciones.splice(idx, 1);
  renderUbicacionesList();
  renderLiveHtmlSheet();
}

function mostrarFormNuevoElemento(ubIdx) {
  sensoresDraft[ubIdx] = [];
  const f = document.getElementById(`formNuevoElem_${ubIdx}`);
  if (f) f.style.display = "block";
  renderSensoresDraft(ubIdx);
}

function ocultarFormNuevoElemento(ubIdx) {
  sensoresDraft[ubIdx] = [];
  const f = document.getElementById(`formNuevoElem_${ubIdx}`);
  if (f) f.style.display = "none";
}

function guardarElementoUbicacion(ubIdx) {
  const tipo = document.getElementById(`elem_tipo_${ubIdx}`).value;
  const nombre = document.getElementById(`elem_nombre_${ubIdx}`).value.trim();
  const serie = document.getElementById(`elem_serie_${ubIdx}`).value.trim();

  const ub = certificadoState.ubicaciones[ubIdx];
  if (!ub.elementos) ub.elementos = [];

  const sensores = sensoresDraft[ubIdx] || [];

  ub.elementos.push({
    tipo: tipo,
    nombre: nombre,
    serie: serie,
    mac: serie,
    sensores: [...sensores]
  });

  sensoresDraft[ubIdx] = [];
  ocultarFormNuevoElemento(ubIdx);
  renderUbicacionesList();
  renderLiveHtmlSheet();
}

function eliminarElementoUbicacion(ubIdx, elIdx) {
  certificadoState.ubicaciones[ubIdx].elementos.splice(elIdx, 1);
  renderUbicacionesList();
  renderLiveHtmlSheet();
}

function renderRepuestosList() {
  const container = document.getElementById("listaRepuestos");
  if (!container) return;

  container.innerHTML = "";
  const repuestos = certificadoState.equipos_repuesto || [];

  if (repuestos.length === 0) {
    container.innerHTML = `<div class="subtitle">No hay equipos de repuesto registrados.</div>`;
    return;
  }

  repuestos.forEach((rep, idx) => {
    const item = document.createElement("div");
    item.className = "repuesto-item";
    const esJennic = (rep.tipo || "").toLowerCase().includes("jennic");
    let identStr = esJennic ? (rep.mac ? ` — MAC: ${rep.mac}` : '') : (` ${rep.metraje ? rep.metraje + 'm' : ''}` + (rep.serie ? ` — S/N: ${rep.serie}` : ''));

    item.innerHTML = `
      <div class="info"><strong>${idx + 1}. ${rep.tipo}</strong>${identStr}</div>
      <button class="btn btn-small btn-secondary" onclick="eliminarRepuesto(${idx})"></button>
    `;
    container.appendChild(item);
  });
}

function renderMotesList() {
  const container = document.getElementById("contenedorMotesList");
  if (!container) return;

  const motes = certificadoState.motes || [];
  if (motes.length === 0) {
    container.innerHTML = `
      <div style="padding: 12px; background: var(--bg-tertiary, #f8fafc); border-radius: 6px; border: 1px dashed var(--border-color, #cbd5e1); font-size: 13px; color: var(--text-muted);">
        No se han detectado equipos Jennic. Pegue la salida del comando <code>cmd motes</code> o <code>cmd status</code> en el <strong>Auto-rellenado Inteligente</strong> para importar la lista de MACs automáticamente.
      </div>
    `;
    return;
  }

  let rowsHtml = "";
  motes.forEach((m, idx) => {
    const moteNo = m.mote || (idx + 1);
    const mac = m.mac || "-";
    const signal = m.signal || "-";
    const lastRx = m.last_rx || "-";
    const asoc = m.asociacion || m.name || `Equipo ${moteNo}`;

    rowsHtml += `
      <tr>
        <td><strong>Mote ${moteNo}</strong></td>
        <td><code>${mac}</code></td>
        <td>${signal}</td>
        <td>${lastRx}</td>
        <td><span class="badge badge-info">${asoc}</span></td>
        <td style="text-align: center;">
          <button class="btn btn-small btn-secondary" onclick="copiarMacAlPortapapeles('${mac}')" title="Copiar MAC">Copiar</button>
        </td>
      </tr>
    `;
  });

  container.innerHTML = `
    <table class="elementos-table">
      <thead>
        <tr>
          <th>N° Mote</th>
          <th>MAC Address</th>
          <th>Señal</th>
          <th>Last Rx</th>
          <th>Asociación / Nombre</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  `;
}

function renderRepuestosMotesDropdown() {
  const sel = document.getElementById("rep_mac_select");
  if (!sel) return;

  const motes = certificadoState.motes || [];
  if (motes.length === 0) {
    sel.innerHTML = `<option value="">-- No hay motes detectados (Pegue cmd motes en autofill) --</option>`;
    return;
  }

  let html = `<option value="">-- Seleccionar MAC de cmd motes (${motes.length} detectados) --</option>`;
  motes.forEach(m => {
    const name = m.asociacion || m.name || `Equipo ${m.mote || ''}`;
    html += `<option value="${m.mac}">Mote ${m.mote || ''}: ${m.mac} (${name})</option>`;
  });
  sel.innerHTML = html;
}

function copiarMacAlPortapapeles(mac) {
  if (!mac) return;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(mac).then(() => {
      mostrarToast(`MAC ${mac} copiada al portapapeles`, "success");
    }).catch(() => {
      mostrarToast(`MAC: ${mac}`, "info");
    });
  } else {
    mostrarToast(`MAC: ${mac}`, "info");
  }
}

function guardarNuevoRepuestoInline() {
  const tipo = document.getElementById("rep_tipo_select").value;
  const esJennic = tipo === "Equipo Jennic";
  const mac = document.getElementById("rep_mac_input").value.trim();
  const serie = document.getElementById("rep_serie_input").value.trim();
  const metraje = document.getElementById("rep_metraje_input").value.trim();

  if (!certificadoState.equipos_repuesto) certificadoState.equipos_repuesto = [];
  certificadoState.equipos_repuesto.push({
    tipo: tipo, cant: 1, cantidad: 1, descripcion: tipo, metraje: esJennic ? "" : metraje,
    mac: esJennic ? mac : "", serie: esJennic ? "" : serie, identificacion: esJennic ? mac : serie,
    ubicacion: certificadoState.ubicacion_repuestos || ""
  });

  document.getElementById("rep_mac_input").value = "";
  document.getElementById("rep_serie_input").value = "";
  document.getElementById("rep_metraje_input").value = "";
  document.getElementById("formNuevoRepuesto").style.display = "none";

  renderRepuestosList();
  renderLiveHtmlSheet();
}

function eliminarRepuesto(idx) {
  certificadoState.equipos_repuesto.splice(idx, 1);
  renderRepuestosList();
  renderLiveHtmlSheet();
}

async function cargarListaCertificadosHeader(autoLoadFirst = false) {
  const headerSel = document.getElementById("headerCertSelect");
  if (!headerSel) return;

  try {
    const res = await fetch("/api/list?año=2026");
    const data = await res.json();
    headerSel.innerHTML = "<option value=''>Cargar Certificado...</option>";

    if (data.status === "ok" && data.certificados.length > 0) {
      data.certificados.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        headerSel.appendChild(opt);
      });

      if (autoLoadFirst && (!certificadoState.datos_generales || !certificadoState.datos_generales.location)) {
        headerSel.value = data.certificados[0];
        await cargarCertificadoPorLocation(data.certificados[0]);
      }
    }
  } catch (err) {
    headerSel.innerHTML = "<option value=''>Error de red</option>";
  }
}

async function cargarCertificadoPorLocation(locationId) {
  try {
    const res = await fetch("/api/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location: locationId, año: 2026 })
    });
    const data = await res.json();

    if (data.status === "ok") {
      certificadoState = data.certificado;
      poblarFormularioDesdeState();
      mostrarToast(`Certificado cargado: ${locationId}`, "success");
    }
  } catch (err) {
    mostrarToast("Error al cargar certificado", "error");
  }
}

async function eliminarCertificadoPorLocation(locationId) {
  try {
    const res = await fetch("/api/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location: locationId, año: 2026 })
    });
    const data = await res.json();

    if (data.status === "ok") {
      crearNuevoCertificadoSinPopup();
      await cargarListaCertificadosHeader(false);
      mostrarToast(data.mensaje || "Certificado eliminado exitosamente.", "success");
    } else {
      mostrarToast(data.mensaje || "Error al eliminar certificado", "error");
    }
  } catch (err) {
    mostrarToast("Error al eliminar certificado: " + err.message, "error");
  }
}

function validarCamposObligatorios() {
  const dg = certificadoState.datos_generales || {};
  const loc = (dg.location || "").trim();
  const nom = (dg.nombre_centro || "").trim();

  if (!loc || !nom) {
    mostrarToast("Location ID y Nombre del Centro son campos obligatorios.", "error");
    const tabBtn = document.querySelector(".tab-btn[data-tab='generales']");
    if (tabBtn) tabBtn.click();
    
    if (!loc) {
      const inputLoc = document.getElementById("gen_location");
      if (inputLoc) inputLoc.focus();
    } else if (!nom) {
      const inputNom = document.getElementById("gen_nombre_centro");
      if (inputNom) inputNom.focus();
    }
    return false;
  }
  return true;
}

// Compilar y Mostrar PDF Oficial
async function compilarYMostrarPDF() {
  if (!validarCamposObligatorios()) return;

  mostrarToast("Compilando PDF Oficial ReportLab...", "info");
  try {
    const res = await fetch("/api/generate_pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ certificado: certificadoState })
    });
    const data = await res.json();

    if (data.status === "ok") {
      document.getElementById("liveHtmlContainer").style.display = "none";
      document.getElementById("pdfContainer").style.display = "flex";
      document.getElementById("btnToggleVistaPDF").classList.add("active");
      document.getElementById("btnToggleVistaHTML").classList.remove("active");

      const frame = document.getElementById("pdfFrame");
      if (frame) frame.src = data.pdf_preview_url + "?t=" + new Date().getTime();
      mostrarToast("PDF Oficial listo.", "success");
    }
  } catch (err) {
    mostrarToast("Error al generar PDF: " + err.message, "error");
  }
}

function abrirVistaPreviaPopout() {
  const loc = certificadoState.datos_generales.location || "ce-tranqui1";
  const url = `/api/pdf_preview/2026/${loc}/certificado_inst_${loc}.pdf`;
  window.open(url, "_blank", "width=900,height=1000");
}

async function procesarAutofill() {
  const texto = document.getElementById("autofillText").value;
  if (!texto.trim()) {
    mostrarToast("Por favor pegue la salida de consola en el cuadro", "warning");
    return;
  }

  try {
    const res = await fetch("/api/autofill", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: texto, certificado: certificadoState })
    });
    const data = await res.json();

    if (data.status === "ok") {
      certificadoState = data.certificado;
      poblarFormularioDesdeState();
      mostrarToast("Documento autorellenado con éxito.", "success");
      
      // Cambiar automáticamente de pestaña: "Auto-relleno Rápido" -> "1. Datos generales"
      activarSeccionTab("generales");
      document.querySelectorAll(".tab-btn").forEach(t => {
        if (t.dataset.tab === "generales") t.classList.add("active");
        else t.classList.remove("active");
      });
    }
  } catch (err) {
    mostrarToast("Error de conexión al parsear datos", "error");
  }
}

async function ejecutarSSHAutofill() {
  const host = document.getElementById("ssh_autofill_host")?.value.trim();
  const usuario = document.getElementById("ssh_autofill_user")?.value.trim() || "innovex";
  const clave = document.getElementById("ssh_autofill_pass")?.value || "CERMAQ@sh20";
  const puerto_ssh = document.getElementById("ssh_autofill_port")?.value.trim() || "22";
  const puerto_telnet = document.getElementById("ssh_autofill_telnet_port")?.value.trim() || "9999";

  if (!host) {
    mostrarToast("Ingrese la IP o DNS del equipo remoto para conectar", "warning");
    return;
  }

  const btn = document.getElementById("btnEjecutarSSHAutofill");
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Conectando...";

  try {
    const res = await fetch("/api/ssh_autofill", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ host, usuario, clave, puerto_ssh, puerto_telnet, certificado: certificadoState })
    });
    const data = await res.json();

    if (data.status === "ok" && data.certificado) {
      certificadoState = data.certificado;
      poblarFormularioDesdeState();
      mostrarToast("Auto-rellenado por SSH/Telnet completado con éxito.", "success");
      
      // Cambiar automáticamente de pestaña: "Auto-relleno Rápido" -> "1. Datos generales"
      activarSeccionTab("generales");
      document.querySelectorAll(".tab-btn").forEach(t => {
        if (t.dataset.tab === "generales") t.classList.add("active");
        else t.classList.remove("active");
      });
    } else {
      mostrarToast(`Error SSH: ${data.mensaje || "No se pudo consultar el equipo remoto"}`, "error");
    }
  } catch (err) {
    mostrarToast(`Error de conexión SSH: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

function copiarComandoPortapapeles() {
  const cmdInput = document.getElementById("codeCommandCopy");
  if (cmdInput) {
    cmdInput.select();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(cmdInput.value).then(() => {
        mostrarToast("Comando copiado al portapapeles", "success");
      });
    } else {
      document.execCommand("copy");
      mostrarToast("Comando copiado", "success");
    }
  }
}

function setupNavButtons() {
  document.addEventListener("click", (e) => {
    const prevBtn = e.target.closest(".nav-prev-btn");
    const nextBtn = e.target.closest(".nav-next-btn");

    if (prevBtn) {
      const targetTab = prevBtn.dataset.prev;
      activarSeccionTab(targetTab);
      document.querySelectorAll(".tab-btn").forEach(t => {
        if (t.dataset.tab === targetTab) t.classList.add("active");
        else t.classList.remove("active");
      });
    } else if (nextBtn) {
      const targetTab = nextBtn.dataset.next;
      activarSeccionTab(targetTab);
      document.querySelectorAll(".tab-btn").forEach(t => {
        if (t.dataset.tab === targetTab) t.classList.add("active");
        else t.classList.remove("active");
      });
    }
  });
}

async function guardarAvance() {
  if (!validarCamposObligatorios()) return;

  try {
    const res = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ certificado: certificadoState })
    });
    const data = await res.json();

    if (data.status === "ok") {
      mostrarToast("Certificado guardado exitosamente.", "success");
      cargarListaCertificadosHeader();
    }
  } catch (err) {
    mostrarToast("Error al guardar", "error");
  }
}

// ----------------------------------------------------
// MÓDULO REVISOR DE EQUIPOS Y VERIFICACIÓN DE INGRESO
// ----------------------------------------------------
let ultimoResultadoRevisor = null;

function setInputValue(id, val) {
  const el = document.getElementById(id);
  if (el && val !== undefined && val !== null && val !== "") {
    el.value = val;
  }
}

async function ejecutarRevisorEquipos() {
  const centro = document.getElementById("rev_centro").value.trim();
  const host = document.getElementById("rev_host").value.trim();
  const usuario = document.getElementById("rev_usuario").value.trim();
  const contrasena = document.getElementById("rev_contrasena").value;
  const puerto_ssh = document.getElementById("rev_puerto_ssh").value.trim();
  const puerto_telnet = document.getElementById("rev_puerto_telnet").value.trim();

  const btn = document.getElementById("btnEjecutarRevisor");
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Ejecutando revisión...";

  try {
    const response = await fetch("/api/revisor/verificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        centro, host, usuario, contrasena, puerto_ssh, puerto_telnet
      })
    });
    const data = await response.json();
    if (data.status === "ok" && data.resultado) {
      const res = data.resultado;
      ultimoResultadoRevisor = res;

      if (res.sistema_operativo) setInputValue("rev_sistema_operativo", res.sistema_operativo);
      if (res.kernel) setInputValue("rev_kernel", res.kernel);
      if (res.clave_pc) setInputValue("rev_clave_pc", res.clave_pc);
      if (res.dataweb) setInputValue("rev_dataweb", res.dataweb);

      if (res.pcinnovex) setInputValue("rev_pcinnovex", res.pcinnovex);
      if (res.cacheton) setInputValue("rev_cacheton", res.cacheton);
      if (res.python3_cacheton) setInputValue("rev_python3", res.python3_cacheton);
      if (res.weather_davis) setInputValue("rev_weather_davis", res.weather_davis);
      if (res.visibility_cam) setInputValue("rev_visibility_cam", res.visibility_cam);

      if (res.version_equipos) setInputValue("rev_version_equipos", res.version_equipos);
      if (res.senal) setInputValue("rev_senal", res.senal);
      if (res.voltajes) setInputValue("rev_voltajes", res.voltajes);

      construirPlantillaRevisorDesdeFormulario();

      if (data.resultado.error) {
        mostrarToast(`Revisión completada con observaciones: ${data.resultado.error}`, "warning");
      } else {
        mostrarToast("Verificación completada y formulario autollenado con éxito", "success");
      }
    } else {
      mostrarToast(`Error: ${data.mensaje || "No se pudo realizar la revisión"}`, "error");
    }
  } catch (err) {
    mostrarToast(`Error al ejecutar revisión: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

function construirPlantillaRevisorDesdeFormulario() {
  const centroRaw = document.getElementById("rev_centro")?.value.trim() || "CE-YELCHO";
  let centroTitulo = centroRaw.toUpperCase();
  if (!centroTitulo.startsWith("CE-") && !centroTitulo.startsWith("MW-") && !centroTitulo.startsWith("CENTRO")) {
    centroTitulo = "CE-" + centroTitulo;
  }

  const tipo_conexion = document.getElementById("rev_tipo_conexion")?.value || "Wifi";
  const sistema_operativo = document.getElementById("rev_sistema_operativo")?.value.trim() || "Linux Ubuntu 20.04 LTS";
  const kernel = document.getElementById("rev_kernel")?.value.trim() || "5.4.0-105-generic";
  const clave_pc = document.getElementById("rev_clave_pc")?.value.trim() || "No configurada";
  const dataweb = document.getElementById("rev_dataweb")?.value.trim() || "Ok";

  function fmtChangeset(val, defaultNum) {
    let str = (val || "").trim();
    if (!str || str.toUpperCase() === "N/A") return `changeset:   ${defaultNum}`;
    const m = str.match(/(\d+)/);
    if (m) return `changeset:   ${m[1]}`;
    return str;
  }

  const pcinnovex = fmtChangeset(document.getElementById("rev_pcinnovex")?.value, "583");
  const cacheton = fmtChangeset(document.getElementById("rev_cacheton")?.value, "631");
  const python3_ver = fmtChangeset(document.getElementById("rev_python3")?.value, "415");
  const weather_davis = document.getElementById("rev_weather_davis")?.value.trim() || "1.1.1";
  const visibility_cam = document.getElementById("rev_visibility_cam")?.value.trim() || "3.6";

  let version_equipos = document.getElementById("rev_version_equipos")?.value.trim() || "v2.0.2";
  if (version_equipos && !version_equipos.startsWith("v") && !version_equipos.startsWith("V")) {
    version_equipos = "v" + version_equipos;
  }

  let senal = document.getElementById("rev_senal")?.value.trim() || "57/198";
  if (senal && !senal.startsWith("igual o mayor a")) {
    senal = "igual o mayor a " + senal;
  }

  let voltajes = document.getElementById("rev_voltajes")?.value.trim() || "3.28V";
  if (voltajes && !voltajes.startsWith("igual o mayor a")) {
    const vVal = voltajes.endsWith("V") || voltajes.endsWith("v") ? voltajes : voltajes + "V";
    voltajes = "igual o mayor a " + vVal;
  }

  const saturacion = document.getElementById("rev_saturacion")?.value.trim() || "OK";
  const salinidad = document.getElementById("rev_salinidad")?.value.trim() || "OK";
  const temperatura = document.getElementById("rev_temperatura")?.value.trim() || "OK";

  const camara = document.getElementById("rev_camara")?.value || "OK";
  const estacion = document.getElementById("rev_estacion")?.value || "OK";

  const repuesto_equipo = document.getElementById("rev_repuesto_equipo")?.value || "";
  const repuesto_sensor = document.getElementById("rev_repuesto_sensor")?.value || "";
  const repuesto_kit = document.getElementById("rev_repuesto_kit")?.value || "";
  const repuestos_texto = document.getElementById("rev_repuestos")?.value.trim() || "";

  let repSec = "7. Repuestos: ";
  if (repuestos_texto) {
    repSec = `7. Repuestos: ${repuestos_texto}`;
  } else if (repuesto_equipo || repuesto_sensor || repuesto_kit) {
    repSec = `7. Repuestos:\n* Equipo: ${repuesto_equipo || 'OK'}\n* Sensor: ${repuesto_sensor || 'OK'}\n* Kit limpieza: ${repuesto_kit || 'OK'}`;
  }

  const telefono = document.getElementById("rev_telefono")?.value.trim() || "";
  const correo = document.getElementById("rev_correo")?.value.trim() || "";

  const obsRaw = document.getElementById("rev_observaciones")?.value.trim() || "";
  let obsFormatted = "- ----";
  if (obsRaw && obsRaw !== "-") {
    const lines = obsRaw.split("\n");
    const formatted = [];
    lines.forEach(l => {
      const lStr = l.trim();
      if (lStr) {
        formatted.push(lStr.startsWith("-") ? lStr : "- " + lStr);
      }
    });
    if (formatted.length > 0) obsFormatted = formatted.join("\n");
  }

  const plantilla =
`VERIFICACIÓN INGRESO  ${centroTitulo}
1. Datos computador:
* Tipo Conexión: ${tipo_conexion}
* Sistema Operativo: ${sistema_operativo}
* Kernel: ${kernel}
* Clave: ${clave_pc}
* Visualización Dataweb: ${dataweb}
2. Paquetería computador:
* pcinnovex: ${pcinnovex}
* cacheton: ${cacheton}
* python3: ${python3_ver}
* Weather Davis: ${weather_davis}
* Visibility-cam: ${visibility_cam}
3. Equipos:
* Versión: ${version_equipos}
* Señal: ${senal}
* Voltajes: ${voltajes}
4. Validación de Variación de Mediciones en Superficie:
* Saturación 95% - 105%:  ${saturacion}
* Salinidad: 0Psu - 1Psu: ${salinidad}
* Temperatura Ambiente: ${temperatura}
5. Cámara: ${camara}
6. Estación: ${estacion}
${repSec}
8. Datos del centro:
* Teléfono: ${telefono}
* Correo: ${correo}
9. Observaciones:
${obsFormatted}`;

  const elTxt = document.getElementById("txtPlantillaRevisor");
  if (elTxt) elTxt.value = plantilla;

  if (moduloActivoActual === "revisor") {
    const btnToggleTexto = document.getElementById("btnToggleVistaTexto");
    if (btnToggleTexto && btnToggleTexto.classList.contains("active")) {
      mostrarTextoPlanoEnPanelDerecho();
    } else {
      mostrarVistaPreviaRevisorDerecha();
    }
  }
}

function generarPlantillaRevisor() {
  construirPlantillaRevisorDesdeFormulario();
}

async function copiarPlantillaRevisor() {
  construirPlantillaRevisorDesdeFormulario();
  const txt = document.getElementById("txtPlantillaRevisor").value;
  if (!txt.trim()) {
    mostrarToast("No hay plantilla para copiar.", "warning");
    return;
  }
  navigator.clipboard.writeText(txt).then(() => {
    mostrarToast("Plantilla copiada al portapapeles con éxito", "success");
  }).catch(() => {
    mostrarToast("No se pudo copiar automáticamente al portapapeles", "error");
  });
}

function actualizarFrameDocumentoLive() {
  const frame = document.getElementById("frameDocumentoLive");
  if (!frame) return;
  if (ultimoResultadoRevisor && ultimoResultadoRevisor.documento_live_html) {
    frame.srcdoc = ultimoResultadoRevisor.documento_live_html;
  } else {
    const centro = document.getElementById("rev_centro").value.trim() || "CE-CENTRO";
    const host = document.getElementById("rev_host").value.trim() || "127.0.0.1";
    const tipo_conexion = document.getElementById("rev_tipo_conexion").value;
    const clave_pc = document.getElementById("rev_clave_pc").value.trim();
    const dataweb = document.getElementById("rev_dataweb").value.trim() || "Ok";
    const saturacion = document.getElementById("rev_saturacion").value.trim() || "OK";
    const salinidad = document.getElementById("rev_salinidad").value.trim() || "OK";
    const temperatura = document.getElementById("rev_temperatura").value.trim() || "OK";

    fetch("/api/revisor/verificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ centro, host, tipo_conexion, clave_pc, dataweb, saturacion, salinidad, temperatura })
    }).then(r => r.json()).then(data => {
      if (data.status === "ok" && data.resultado) {
        ultimoResultadoRevisor = data.resultado;
        frame.srcdoc = data.resultado.documento_live_html || "";
      }
    });
  }
}


function autoRellenarDesdeRevisor() {
  if (!ultimoResultadoRevisor) {
    const centro = document.getElementById("rev_centro").value.trim();
    if (centro) {
      if (!certificadoState.datos_generales) certificadoState.datos_generales = {};
      certificadoState.datos_generales.location = centro.toLowerCase().replace(/[^a-z0-9_-]/g, "");
      certificadoState.datos_generales.nombre_centro = centro.toUpperCase();
      poblarFormularioDesdeState();
      mostrarToast("Datos principales actualizados en la ficha del certificado", "success");
    } else {
      mostrarToast("Ingrese al menos el nombre del centro para autorellenar", "warning");
    }
    return;
  }

  const r = ultimoResultadoRevisor;
  if (!certificadoState.datos_generales) certificadoState.datos_generales = {};
  if (r.centro) {
    certificadoState.datos_generales.location = r.centro.toLowerCase().replace(/[^a-z0-9_-]/g, "");
    certificadoState.datos_generales.nombre_centro = r.centro.toUpperCase();
  }
  poblarFormularioDesdeState();
  mostrarToast("Ficha de certificado actualizada desde el Revisor", "success");
}

async function actualizarVistaPreviaHTMLRevisor() {
  const liveSheet = document.getElementById("liveHtmlSheet");
  if (!liveSheet) return;

  const centro = document.getElementById("rev_centro")?.value.trim() || "CE-YELCHO";
  const host = document.getElementById("rev_host")?.value.trim() || "";
  const tipo_conexion = document.getElementById("rev_tipo_conexion")?.value || "Wifi";
  const sistema_operativo = document.getElementById("rev_sistema_operativo")?.value.trim() || "Linux Ubuntu 20.04 LTS";
  const kernel = document.getElementById("rev_kernel")?.value.trim() || "5.4.0-105-generic";
  const clave_pc = document.getElementById("rev_clave_pc")?.value.trim() || "No configurada";
  const dataweb = document.getElementById("rev_dataweb")?.value.trim() || "Ok";

  const pcinnovex = document.getElementById("rev_pcinnovex")?.value.trim() || "changeset:   583";
  const cacheton = document.getElementById("rev_cacheton")?.value.trim() || "changeset:   631";
  const python3_cacheton = document.getElementById("rev_python3")?.value.trim() || "changeset:   415";
  const weather_davis = document.getElementById("rev_weather_davis")?.value.trim() || "1.1.1";
  const visibility_cam = document.getElementById("rev_visibility_cam")?.value.trim() || "3.6";

  const version_equipos = document.getElementById("rev_version_equipos")?.value.trim() || "v2.0.2";
  const senal = document.getElementById("rev_senal")?.value.trim() || "57/198";
  const voltajes = document.getElementById("rev_voltajes")?.value.trim() || "3.28V";

  const saturacion = document.getElementById("rev_saturacion")?.value.trim() || "OK";
  const salinidad = document.getElementById("rev_salinidad")?.value.trim() || "OK";
  const temperatura = document.getElementById("rev_temperatura")?.value.trim() || "OK";

  const camara = document.getElementById("rev_camara")?.value || "OK";
  const estacion = document.getElementById("rev_estacion")?.value || "OK";

  const repuestos = document.getElementById("rev_repuestos")?.value.trim() || "";
  const repuesto_equipo = document.getElementById("rev_repuesto_equipo")?.value || "";
  const repuesto_sensor = document.getElementById("rev_repuesto_sensor")?.value || "";
  const repuesto_kit = document.getElementById("rev_repuesto_kit")?.value || "";

  const telefono = document.getElementById("rev_telefono")?.value.trim() || "";
  const correo = document.getElementById("rev_correo")?.value.trim() || "";
  const observaciones = document.getElementById("rev_observaciones")?.value || "";

  const nodos_detalle = ultimoResultadoRevisor?.nodos_detalle || [];
  const motes_texto_raw = ultimoResultadoRevisor?.motes_texto_raw || "";
  const salida_status = ultimoResultadoRevisor?.salida_status || "";

  try {
    const response = await fetch("/api/revisor/verificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        centro, host, tipo_conexion, sistema_operativo, kernel, clave_pc, dataweb,
        pcinnovex, cacheton, python3_cacheton, weather_davis, visibility_cam,
        version_equipos, senal, voltajes,
        saturacion, salinidad, temperatura,
        camara, estacion, repuestos, repuesto_equipo, repuesto_sensor, repuesto_kit,
        telefono, correo, observaciones,
        nodos_detalle, motes_texto_raw, salida_status
      })
    });
    const data = await response.json();
    if (data.status === "ok" && data.resultado) {
      ultimoResultadoRevisor = data.resultado;
      const htmlDoc = data.resultado.documento_live_html || "";
      liveSheet.innerHTML = `<iframe srcdoc="${htmlEscapeAttr(htmlDoc)}" style="width: 100%; height: 850px; border: none; border-radius: 8px;" title="Live Revisor"></iframe>`;
    }
  } catch (err) {
    console.error("Error al actualizar HTML Live Revisor:", err);
  }
}

function mostrarVistaPreviaRevisorDerecha() {
  actualizarVistaPreviaHTMLRevisor();
}

function mostrarTextoPlanoEnPanelDerecho() {
  const liveSheet = document.getElementById("liveHtmlSheet");
  if (!liveSheet) return;

  document.getElementById("liveHtmlContainer").style.display = "flex";
  document.getElementById("pdfContainer").style.display = "none";
  document.getElementById("btnToggleVistaHTML").classList.remove("active");
  if (document.getElementById("btnToggleVistaPDF")) document.getElementById("btnToggleVistaPDF").classList.remove("active");
  if (document.getElementById("btnToggleVistaTexto")) document.getElementById("btnToggleVistaTexto").classList.add("active");

  let textoPlano = "";
  if (moduloActivoActual === "revisor") {
    textoPlano = document.getElementById("txtPlantillaRevisor") ? document.getElementById("txtPlantillaRevisor").value : "";
    if (!textoPlano && ultimoResultadoRevisor && ultimoResultadoRevisor.plantilla_texto) {
      textoPlano = ultimoResultadoRevisor.plantilla_texto;
    }
  } else if (moduloActivoActual === "ingreso_tecnico") {
    textoPlano = document.getElementById("txtPlantillaIngresoTecnico").value;
    if (!textoPlano && ultimoResultadoIngreso && ultimoResultadoIngreso.plantilla_texto) {
      textoPlano = ultimoResultadoIngreso.plantilla_texto;
    }
  }

  liveSheet.innerHTML = `
    <div style="background: #ffffff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-height: 800px; font-family: sans-serif;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 2px solid #002d4b; padding-bottom: 8px;">
        <h3 style="margin: 0; color: #002d4b; font-size: 16px; text-transform: uppercase;">Vista Texto Plano</h3>
        <button class="btn btn-small btn-secondary" onclick="navigator.clipboard.writeText(document.getElementById('preTextoPlanoDerecho').innerText); mostrarToast('Texto plano copiado', 'success');">Copiar Texto</button>
      </div>
      <pre id="preTextoPlanoDerecho" style="background: #1e293b; color: #f8fafc; padding: 16px; border-radius: 6px; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; line-height: 1.5; overflow-x: auto; white-space: pre-wrap; word-break: break-word;">${htmlEscapeAttr(textoPlano || "Sin texto disponible.")}</pre>
    </div>
  `;
}

function htmlEscapeAttr(str) {
  if (!str) return "";
  return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// MÓDULO INFORMACIÓN PARA INGRESO DE TÉCNICO
let ultimoResultadoIngreso = null;

const PLANTILLA_OBS_GENERALES_DEFAULT = `Actualizar paquetería PC

Fotos de los repuestos en su ubicación final
    Bolso Innovex
    Equipo con su tapa y pantalla visible
    Sensor/es de repuesto con vista a su S/N, cabezal y tapa protectora


Fotos notebook/otros
    Entradas USB, cualquier conexión conectada/ocupada
    Componentes (Switch POE/Hub, antena, meteo-stick entre otros)
    Tomas de corriente
Fotos equipos transmisores
    Pantallas visibles
    Pedestales con metrajes claros
    Sin tapa (si es que la climática lo permite)
Información acerca del tipo de estación y cámara
Corroborar u obtener datos del centro, teléfono y correo electrónico.`;

function inicializarObservacionesGeneralesDefault() {
  const el = document.getElementById("ingreso_observaciones_generales");
  if (el && !el.value.trim()) {
    el.value = PLANTILLA_OBS_GENERALES_DEFAULT;
  }
}

function prellenarDatosHostIngresoTecnico() {
  // Dejar espacio en blanco por defecto como solicitó el usuario
}

async function ejecutarIngresoTecnico() {
  const host = document.getElementById("ingreso_host").value.trim();
  const usuario = document.getElementById("ingreso_usuario").value.trim() || "innovex";
  const contrasena = document.getElementById("ingreso_contrasena").value;
  const clave_pc = document.getElementById("ingreso_clave_pc").value.trim() || contrasena || "No configurada";
  document.getElementById("ingreso_clave_pc").value = clave_pc;

  const acceso_remoto = document.getElementById("ingreso_acceso_remoto").value.trim();
  const repuestos_equipo = document.getElementById("ingreso_repuesto_equipo")?.value || "OK";
  const repuestos_sensor = document.getElementById("ingreso_repuesto_sensor")?.value || "OK";
  const repuestos_kit = document.getElementById("ingreso_repuesto_kit")?.value || "OK";

  const observaciones = document.getElementById("ingreso_observaciones").value;
  const observaciones_generales = document.getElementById("ingreso_observaciones_generales").value;

  const btn = document.getElementById("btnEjecutarIngresoTecnico");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = "Consultando / Generando...";
  }

  try {
    const response = await fetch("/api/revisor/ingreso_tecnico", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        host,
        usuario,
        contrasena,
        clave_pc,
        acceso_remoto,
        repuestos_equipo,
        repuestos_sensor,
        repuestos_kit,
        observaciones,
        observaciones_generales
      })
    });
    const data = await response.json();
    if (data.status === "ok" && data.resultado) {
      const res = data.resultado;
      ultimoResultadoIngreso = res;

      if (res.antena_status) document.getElementById("ingreso_antena_status").value = res.antena_status;
      if (res.equipos_conectados) document.getElementById("ingreso_equipos_conectados").value = res.equipos_conectados;
      if (res.voltaje_pilas) document.getElementById("ingreso_voltaje_pilas").value = res.voltaje_pilas;
      if (res.dns !== undefined) document.getElementById("ingreso_host").value = res.dns;
      if (res.clave_pc) document.getElementById("ingreso_clave_pc").value = res.clave_pc;

      document.getElementById("txtPlantillaIngresoTecnico").value = res.plantilla_texto || "";
      actualizarFrameDocumentoIngresoLive();
      actualizarVistaPreviaDerechaPorModulo();

      mostrarToast("Información para ingreso de técnico cargada con éxito", "success");
    } else {
      mostrarToast("" + (data.mensaje || "Error al procesar consulta"), "error");
    }
  } catch (err) {
    console.error("Error en consulta ingreso técnico:", err);
    mostrarToast("Error de red o servidor al ejecutar consulta", "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = "Consultar Remotamente (SSH / Telnet)";
    }
  }
}

async function generarPlantillaIngreso() {
  const host = document.getElementById("ingreso_host").value.trim();
  const clave_pc = document.getElementById("ingreso_clave_pc").value.trim() || "No configurada";
  document.getElementById("ingreso_clave_pc").value = clave_pc;

  const acceso_remoto = document.getElementById("ingreso_acceso_remoto").value.trim();
  const repuestos_equipo = document.getElementById("ingreso_repuesto_equipo")?.value || "OK";
  const repuestos_sensor = document.getElementById("ingreso_repuesto_sensor")?.value || "OK";
  const repuestos_kit = document.getElementById("ingreso_repuesto_kit")?.value || "OK";

  const antena_status = document.getElementById("ingreso_antena_status").value;
  const equipos_conectados = document.getElementById("ingreso_equipos_conectados").value;
  const voltaje_pilas = document.getElementById("ingreso_voltaje_pilas").value;
  const observaciones = document.getElementById("ingreso_observaciones").value;
  const observaciones_generales = document.getElementById("ingreso_observaciones_generales").value;

  try {
    const response = await fetch("/api/revisor/generar_plantilla_ingreso", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dns: host,
        clave_pc,
        acceso_remoto,
        repuestos_equipo,
        repuestos_sensor,
        repuestos_kit,
        antena_status,
        equipos_conectados,
        voltaje_pilas,
        observaciones,
        observaciones_generales
      })
    });
    const data = await response.json();
    if (data.status === "ok") {
      document.getElementById("txtPlantillaIngresoTecnico").value = data.plantilla_texto || "";
      ultimoResultadoIngreso = {
        dns: host,
        clave_pc,
        acceso_remoto,
        repuestos_equipo,
        repuestos_sensor,
        repuestos_kit,
        antena_status,
        equipos_conectados,
        voltaje_pilas,
        observaciones,
        observaciones_generales,
        plantilla_texto: data.plantilla_texto,
        documento_live_html: data.documento_live_html
      };
      actualizarFrameDocumentoIngresoLive();
      actualizarVistaPreviaDerechaPorModulo();
      mostrarToast("Plantilla y Documento Live actualizados", "success");
    }
  } catch (err) {
    console.error("Error al generar plantilla ingreso:", err);
  }
}

function actualizarFrameDocumentoIngresoLive() {
  const frame = document.getElementById("frameDocumentoIngresoLive");
  if (frame && ultimoResultadoIngreso && ultimoResultadoIngreso.documento_live_html) {
    frame.srcdoc = ultimoResultadoIngreso.documento_live_html;
  }
}

function mostrarVistaPreviaIngresoDerecha() {
  const liveSheet = document.getElementById("liveHtmlSheet");
  if (!liveSheet) return;

  if (ultimoResultadoIngreso && ultimoResultadoIngreso.documento_live_html) {
    liveSheet.innerHTML = `<iframe srcdoc="${htmlEscapeAttr(ultimoResultadoIngreso.documento_live_html)}" style="width: 100%; height: 850px; border: none; border-radius: 8px;" title="Live Ingreso Técnico"></iframe>`;
  } else {
    liveSheet.innerHTML = `<div style="padding: 40px; text-align: center; color: #64748b; font-family: sans-serif;">Generando vista previa de Ingreso Técnico...</div>`;
    generarPlantillaIngreso();
  }
}

function copiarPlantillaIngreso() {
  let txt = document.getElementById("txtPlantillaIngresoTecnico").value;
  if (!txt.trim()) {
    generarPlantillaIngreso();
    setTimeout(() => {
      txt = document.getElementById("txtPlantillaIngresoTecnico").value;
      if (txt) {
        navigator.clipboard.writeText(txt).then(() => {
          mostrarToast("Plantilla de Ingreso de Técnico copiada al portapapeles", "success");
        });
      }
    }, 250);
  } else {
    navigator.clipboard.writeText(txt).then(() => {
      mostrarToast("Plantilla de Ingreso de Técnico copiada al portapapeles", "success");
    });
  }
}
