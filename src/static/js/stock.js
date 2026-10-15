// ============================================
// stock.js - Lógica de la página de stock
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const rol = getUserRol();
    const isAdmin = rol === 'admin';
    const isSupervisor = rol === 'supervisor';
    const puedeEditar = isAdmin || isSupervisor;
    
    // Mostrar/ocultar botones según rol
    if (puedeEditar) {
        document.getElementById('btnNuevoProducto').style.display = 'inline-block';
        document.getElementById('btnNuevaCategoria').style.display = 'inline-block';
    }
    
    if (rol === 'admin' || rol === 'supervisor') {
        const reporteLink = document.getElementById('reporteLink');
        if (reporteLink) {
            reporteLink.style.display = 'inline';
            reporteLink.href = '/reporte.html';
        }
    }
    
    // Cargar datos iniciales
    loadTasasIva();
    loadCategorias();
    loadProductos();
    loadAlertas();
    
    // Event listeners
    document.getElementById('btnNuevoProducto').addEventListener('click', () => {
        document.getElementById('productoModalTitle').textContent = 'Nuevo Producto';
        document.getElementById('productoForm').reset();
        document.getElementById('productoId').value = '';
        document.getElementById('productoModal').style.display = 'flex';
    });
    
    document.getElementById('btnNuevaCategoria').addEventListener('click', () => {
        document.getElementById('categoriaForm').reset();
        document.getElementById('categoriaModal').style.display = 'flex';
    });
    
    document.getElementById('productoForm').addEventListener('submit', handleProductoSubmit);
    document.getElementById('movimientoForm').addEventListener('submit', handleMovimientoSubmit);
    document.getElementById('categoriaForm').addEventListener('submit', handleCategoriaSubmit);
    
    document.getElementById('btnCancelarProducto').addEventListener('click', closeModals);
    document.getElementById('btnCancelarCategoria').addEventListener('click', closeModals);
    document.getElementById('btnCancelarMovimiento').addEventListener('click', closeModals);
    
    document.getElementById('searchInput').addEventListener('input', () => loadProductos());
    document.getElementById('categoriaFilter').addEventListener('change', () => loadProductos());
    document.getElementById('stockBajoFilter').addEventListener('change', () => loadProductos());
    
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        logout();
    });
});

// ============================================
// FUNCIONES DE CARGA DE DATOS
// ============================================

async function loadTasasIva() {
    try {
        const result = await apiRequest('/stock/tasas-iva');
        const select = document.getElementById('prodIva');
        if (select) {
            select.innerHTML = '';
            result.data.forEach(tasa => {
                const option = document.createElement('option');
                option.value = tasa.porcentaje;
                option.textContent = `${tasa.nombre} (${tasa.porcentaje}%)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error cargando tasas IVA:', error);
    }
}

async function loadCategorias() {
    try {
        const result = await apiRequest('/stock/categorias');
        const catSelect = document.getElementById('prodCategoria');
        const catFilter = document.getElementById('categoriaFilter');
        
        catSelect.innerHTML = '<option value="">Sin categoría</option>';
        catFilter.innerHTML = '<option value="">Todas las categorías</option>';
        
        result.data.forEach(cat => {
            catSelect.innerHTML += `<option value="${cat.id}">${cat.nombre}</option>`;
            catFilter.innerHTML += `<option value="${cat.id}">${cat.nombre}</option>`;
        });
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function loadProductos() {
    const search = document.getElementById('searchInput').value;
    const categoriaId = document.getElementById('categoriaFilter').value;
    const stockBajo = document.getElementById('stockBajoFilter').checked;
    
    let url = '/stock/productos?';
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (categoriaId) url += `categoria_id=${categoriaId}&`;
    if (stockBajo) url += `stock_bajo=true&`;
    
    try {
        const result = await apiRequest(url);
        const tbody = document.querySelector('#productosTable tbody');
        tbody.innerHTML = '';
        
        const puedeEditar = getUserRol() === 'admin' || getUserRol() === 'supervisor';
        
        result.data.forEach(p => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = p.id;
            row.insertCell(1).textContent = p.nombre;
            row.insertCell(2).textContent = p.categoria_nombre || '-';
            
            const stockClass = p.stock_actual <= p.stock_minimo ? 'stock-bajo' : 'stock-normal';
            row.insertCell(3).innerHTML = `<span class="${stockClass}">${p.stock_actual}</span>`;
            row.insertCell(4).textContent = p.stock_minimo;
            row.insertCell(5).textContent = `$${p.precio_venta}`;
            
            const actions = row.insertCell(6);
            if (puedeEditar) {
                const editBtn = document.createElement('button');
                editBtn.textContent = 'Editar';
                editBtn.onclick = () => editProducto(p);
                actions.appendChild(editBtn);
                
                const stockBtn = document.createElement('button');
                stockBtn.textContent = 'Stock';
                stockBtn.style.marginLeft = '5px';
                stockBtn.onclick = () => openMovimientoModal(p);
                actions.appendChild(stockBtn);
            }
        });
    } catch (error) {
        console.error('Error cargando productos:', error);
    }
}

async function loadAlertas() {
    try {
        const result = await apiRequest('/stock/alertas');
        const container = document.getElementById('alertasContainer');
        container.innerHTML = '';
        
        if (result.data.length === 0) {
            container.innerHTML = '<div class="alert-card">✅ No hay productos con stock bajo</div>';
        } else {
            result.data.forEach(p => {
                const div = document.createElement('div');
                div.className = p.stock_actual === 0 ? 'alert-card critico' : 'alert-card';
                div.innerHTML = `
                    <strong>${p.nombre}</strong><br>
                    Stock actual: ${p.stock_actual} | Mínimo: ${p.stock_minimo}<br>
                    <small>${p.categoria_nombre || 'Sin categoría'}</small>
                `;
                container.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error cargando alertas:', error);
    }
}

// ============================================
// FUNCIONES DE EDICIÓN Y MODALES
// ============================================

function editProducto(producto) {
    document.getElementById('productoModalTitle').textContent = 'Editar Producto';
    document.getElementById('productoId').value = producto.id;
    document.getElementById('prodNombre').value = producto.nombre;
    document.getElementById('prodDescripcion').value = producto.descripcion || '';
    document.getElementById('prodCategoria').value = producto.categoria_id || '';
    document.getElementById('prodPrecioCompra').value = producto.precio_compra;
    document.getElementById('prodPrecioVenta').value = producto.precio_venta;
    document.getElementById('prodStockActual').value = producto.stock_actual;
    document.getElementById('prodStockMinimo').value = producto.stock_minimo;
    document.getElementById('prodUnidad').value = producto.unidad_medida || 'unidad';
    document.getElementById('prodCodigo').value = producto.codigo_barras || '';
    document.getElementById('prodIva').value = producto.iva_porcentaje || 21.0;
    document.getElementById('productoModal').style.display = 'flex';
}

function openMovimientoModal(producto) {
    document.getElementById('movProductoId').value = producto.id;
    document.getElementById('movProductoNombre').textContent = 
        `${producto.nombre} (Stock actual: ${producto.stock_actual})`;
    document.getElementById('movimientoForm').reset();
    document.getElementById('movimientoModal').style.display = 'flex';
}

function closeModals() {
    document.getElementById('productoModal').style.display = 'none';
    document.getElementById('categoriaModal').style.display = 'none';
    document.getElementById('movimientoModal').style.display = 'none';
}

// ============================================
// MANEJADORES DE FORMULARIOS
// ============================================

async function handleProductoSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('productoId').value;
    const data = {
        nombre: document.getElementById('prodNombre').value,
        descripcion: document.getElementById('prodDescripcion').value,
        categoria_id: document.getElementById('prodCategoria').value || null,
        precio_compra: parseFloat(document.getElementById('prodPrecioCompra').value),
        precio_venta: parseFloat(document.getElementById('prodPrecioVenta').value),
        stock_actual: parseInt(document.getElementById('prodStockActual').value) || 0,
        stock_minimo: parseInt(document.getElementById('prodStockMinimo').value) || 0,
        unidad_medida: document.getElementById('prodUnidad').value,
        codigo_barras: document.getElementById('prodCodigo').value || null,
        iva_porcentaje: parseFloat(document.getElementById('prodIva').value) || 21.0
    };
    
    try {
        if (id) {
            await apiRequest(`/stock/productos/${id}`, 'PUT', data);
        } else {
            await apiRequest('/stock/productos', 'POST', data);
        }
        document.getElementById('productoModal').style.display = 'none';
        loadProductos();
        loadAlertas();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function handleMovimientoSubmit(e) {
    e.preventDefault();
    const data = {
        producto_id: parseInt(document.getElementById('movProductoId').value),
        tipo: document.getElementById('movTipo').value,
        cantidad: parseInt(document.getElementById('movCantidad').value),
        motivo: document.getElementById('movMotivo').value
    };
    
    try {
        await apiRequest('/stock/movimientos', 'POST', data);
        document.getElementById('movimientoModal').style.display = 'none';
        loadProductos();
        loadAlertas();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function handleCategoriaSubmit(e) {
    e.preventDefault();
    const data = {
        nombre: document.getElementById('catNombre').value,
        descripcion: document.getElementById('catDescripcion').value
    };
    
    try {
        await apiRequest('/stock/categorias', 'POST', data);
        document.getElementById('categoriaModal').style.display = 'none';
        loadCategorias();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}