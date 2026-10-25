let productosCache = [];

document.addEventListener('DOMContentLoaded', function() {
    const rol = getUserRol();
    const puedeEditar = rol === 'admin' || rol === 'supervisor';
    
    if (puedeEditar) {
        document.getElementById('btnNuevoProducto').style.display = 'inline-block';
        document.getElementById('btnNuevaCategoria').style.display = 'inline-block';
    }
    
    // Cargar datos iniciales
    loadTasasIva();
    loadCategorias();
    loadProductos();
    loadAlertas();
    
    // Event listeners Modales
    document.getElementById('btnNuevoProducto').addEventListener('click', () => {
        document.getElementById('productoModalTitle').textContent = 'Nuevo Producto';
        document.getElementById('productoForm').reset();
        document.getElementById('productoId').value = '';
        document.getElementById('productoModal').classList.add('show');
        document.getElementById('productoModal').style.display = 'block';
    });
    
    document.getElementById('btnNuevaCategoria').addEventListener('click', () => {
        document.getElementById('categoriaForm').reset();
        document.getElementById('categoriaModal').classList.add('show');
        document.getElementById('categoriaModal').style.display = 'block';
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
});

function closeModals() {
    document.getElementById('productoModal').classList.remove('show');
    document.getElementById('productoModal').style.display = 'none';
    document.getElementById('categoriaModal').classList.remove('show');
    document.getElementById('categoriaModal').style.display = 'none';
    document.getElementById('movimientoModal').classList.remove('show');
    document.getElementById('movimientoModal').style.display = 'none';
}

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
    
    const tbody = document.querySelector('#productosTable tbody');
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</td></tr>';

    try {
        const result = await apiRequest(url);
        productosCache = result.data;
        tbody.innerHTML = '';
        
        const puedeEditar = getUserRol() === 'admin' || getUserRol() === 'supervisor';
        
        if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No se encontraron productos.</td></tr>';
            return;
        }

        result.data.forEach(p => {
            const row = tbody.insertRow();
            row.insertCell(0).innerHTML = `<span class="text-muted">#${p.id}</span>`;
            row.insertCell(1).innerHTML = `<div class="fw-bold">${p.nombre}</div>`;
            row.insertCell(2).textContent = p.categoria_nombre || '-';
            
            const stockClass = p.stock_actual <= p.stock_minimo ? 'stock-bajo' : 'stock-normal';
            row.insertCell(3).innerHTML = `<span class="${stockClass}">${p.stock_actual}</span>`;
            row.insertCell(4).textContent = p.stock_minimo;
            row.insertCell(5).innerHTML = `<span class="text-success fw-bold">$${p.precio_venta}</span>`;
            
            const actions = row.insertCell(6);
            actions.className = 'text-center';
            
            if (puedeEditar) {
                const editBtn = document.createElement('button');
                editBtn.className = 'btn btn-sm btn-outline-primary me-1';
                editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
                editBtn.onclick = () => editProducto(p);
                actions.appendChild(editBtn);
                
                const stockBtn = document.createElement('button');
                stockBtn.className = 'btn btn-sm btn-outline-success';
                stockBtn.innerHTML = '<i class="bi bi-box-seam"></i>';
                stockBtn.onclick = () => openMovimientoModal(p);
                actions.appendChild(stockBtn);
            }
        });
    } catch (error) {
        console.error('Error cargando productos:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Error al cargar datos.</td></tr>`;
    }
}

async function loadAlertas() {
    try {
        const result = await apiRequest('/stock/alertas');
        const container = document.getElementById('alertasContainer');
        container.innerHTML = '';
        
        if (result.data.length === 0) {
            container.innerHTML = '<div class="alert alert-success py-2 mb-0"><i class="bi bi-check-circle me-1"></i> Todo el stock está al día.</div>';
        } else {
            result.data.forEach(p => {
                const div = document.createElement('div');
                div.className = p.stock_actual === 0 ? 'alert-card critico' : 'alert-card';
                div.innerHTML = `
                    <div class="d-flex justify-content-between">
                        <strong>${p.nombre}</strong>
                        <span class="badge bg-dark">${p.stock_actual} un.</span>
                    </div>
                    <small class="text-muted">${p.categoria_nombre || 'Sin categoría'}</small>
                `;
                container.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error cargando alertas:', error);
    }
}

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
    
    const ivaSelect = document.getElementById('prodIva');
    if (ivaSelect) ivaSelect.value = producto.iva_porcentaje ?? 21.0;
    
    document.getElementById('productoModal').classList.add('show');
    document.getElementById('productoModal').style.display = 'block';
}

function openMovimientoModal(producto) {
    document.getElementById('movProductoId').value = producto.id;
    document.getElementById('movProductoNombre').value = producto.nombre;
    document.getElementById('movStockActual').value = producto.stock_actual;
    document.getElementById('movimientoForm').reset();
    document.getElementById('movimientoModal').classList.add('show');
    document.getElementById('movimientoModal').style.display = 'block';
}

async function handleProductoSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('productoId').value;
    const ivaSelect = document.getElementById('prodIva');
    const ivaPorcentaje = ivaSelect ? (parseFloat(ivaSelect.value) || 21.0) : 21.0;
    
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
        iva_porcentaje: ivaPorcentaje
    };
    
    try {
        if (id) {
            await apiRequest(`/stock/productos/${id}`, 'PUT', data);
        } else {
            await apiRequest('/stock/productos', 'POST', data);
        }
        closeModals();
        loadProductos();
        loadAlertas();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function handleMovimientoSubmit(e) {
    e.preventDefault();
    
    const productoId = parseInt(document.getElementById('movProductoId').value);
    const tipo = document.getElementById('movTipo').value;
    const cantidad = parseInt(document.getElementById('movCantidad').value);
    const motivo = document.getElementById('movMotivo').value;
    
    if (tipo === 'salida') {
        const producto = productosCache.find(p => p.id === productoId);
        if (producto && cantidad > producto.stock_actual) {
            alert(`Stock insuficiente. Disponible: ${producto.stock_actual}`);
            return;
        }
    }
    
    try {
        await apiRequest('/stock/movimientos', 'POST', { producto_id: productoId, tipo, cantidad, motivo });
        closeModals();
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
        closeModals();
        loadCategorias();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}