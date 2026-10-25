let productos = [];
let carrito = [];

document.addEventListener('DOMContentLoaded', () => {
    // 1. Cargar Categorías
    loadCategorias();

    // 2. Cargar Productos
    loadProductos();

    // 3. Event Listeners
    document.getElementById('searchProducto').addEventListener('input', (e) => {
        loadProductos(e.target.value, document.getElementById('categoriaVentaFilter').value);
    });

    document.getElementById('categoriaVentaFilter').addEventListener('change', (e) => {
        loadProductos(document.getElementById('searchProducto').value, e.target.value);
    });

    document.getElementById('btnFinalizarVenta').addEventListener('click', finalizarVenta);
    document.getElementById('btnCancelarVenta').addEventListener('click', () => {
        if (carrito.length > 0 && confirm('¿Cancelar la venta actual?')) {
            carrito = [];
            actualizarCarrito();
        }
    });
});

async function loadCategorias() {
    try {
        const result = await apiRequest('/stock/categorias');
        const catFilter = document.getElementById('categoriaVentaFilter');
        result.data.forEach(cat => {
            catFilter.innerHTML += `<option value="${cat.id}">${cat.nombre}</option>`;
        });
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function loadProductos(search = '', categoriaId = '') {
    let url = '/stock/productos?';
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (categoriaId) url += `categoria_id=${categoriaId}&`;

    const container = document.getElementById('listaProductos');
    container.innerHTML = '<div class="col-12 text-center py-4"><span class="spinner-border text-primary"></span></div>';

    try {
        const result = await apiRequest(url);
        productos = result.data;
        container.innerHTML = '';

        if (productos.length === 0) {
            container.innerHTML = '<div class="col-12 text-center text-muted py-4">No se encontraron productos.</div>';
            return;
        }

        productos.forEach(p => {
            if (p.stock_actual > 0) { // Solo mostrar si hay stock
                const col = document.createElement('div');
                col.className = 'col-md-4 col-lg-3 mb-3';
                col.innerHTML = `
                    <div class="card producto-card h-100 p-3" onclick="agregarAlCarrito(${p.id})">
                        <div class="fw-bold text-truncate">${p.nombre}</div>
                        <div class="producto-precio mt-2">$${p.precio_venta}</div>
                        <div class="producto-stock mt-auto pt-2">
                            <i class="bi bi-box"></i> Stock: ${p.stock_actual} ${p.unidad_medida || 'un.'}
                        </div>
                    </div>
                `;
                container.appendChild(col);
            }
        });
        
        if (container.innerHTML === '') {
            container.innerHTML = '<div class="col-12 text-center text-muted py-4">No hay productos con stock disponible en esta categoría.</div>';
        }
    } catch (error) {
        console.error('Error cargando productos:', error);
        container.innerHTML = `<div class="col-12 text-danger">Error: ${error.message}</div>`;
    }
}

window.agregarAlCarrito = function(productoId) {
    const producto = productos.find(p => p.id === productoId);
    if (!producto) return;

    const existing = carrito.find(item => item.id === productoId);
    if (existing) {
        if (existing.cantidad + 1 > producto.stock_actual) {
            alert(`Stock insuficiente. Solo hay ${producto.stock_actual} unidades.`);
            return;
        }
        existing.cantidad += 1;
    } else {
        carrito.push({
            id: productoId,
            nombre: producto.nombre,
            precio: parseFloat(producto.precio_venta),
            cantidad: 1,
            stock_max: producto.stock_actual
        });
    }
    actualizarCarrito();
};

function actualizarCarrito() {
    const container = document.getElementById('carritoItems');
    const btnFinalizar = document.getElementById('btnFinalizarVenta');
    let total = 0;
    
    container.innerHTML = '';

    if (carrito.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4"><i class="bi bi-cart-x fs-2 d-block mb-2"></i>El carrito está vacío</div>';
        document.getElementById('totalCarrito').textContent = '0.00';
        btnFinalizar.disabled = true;
        return;
    }

    btnFinalizar.disabled = false;

    carrito.forEach((item, index) => {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;
        
        const div = document.createElement('div');
        div.className = 'carrito-item';
        div.innerHTML = `
            <div class="flex-grow-1">
                <div class="fw-bold text-truncate" style="max-width: 150px;">${item.nombre}</div>
                <div class="text-muted small">$${item.precio} x ${item.cantidad}</div>
            </div>
            <div class="d-flex align-items-center gap-2">
                <span class="fw-bold">$${subtotal.toFixed(2)}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarDelCarrito(${index})">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(div);
    });

    document.getElementById('totalCarrito').textContent = total.toFixed(2);
}

window.eliminarDelCarrito = function(index) {
    carrito.splice(index, 1);
    actualizarCarrito();
};

async function finalizarVenta() {
    if (carrito.length === 0) return;

    const btn = document.getElementById('btnFinalizarVenta');
    const msgDiv = document.getElementById('ventaMensaje');
    const cliente = document.getElementById('clienteNombre').value || 'Consumidor Final';
    const metodoPago = document.getElementById('metodoPago').value;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';

    const venta = {
        productos: carrito.map(item => ({ producto_id: item.id, cantidad: item.cantidad })),
        cliente_nombre: cliente,
        metodo_pago: metodoPago
    };

    try {
        const result = await apiRequest('/ventas/', 'POST', venta);
        
        msgDiv.className = 'alert alert-success shadow-sm';
        msgDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1 fw-bold">¡Venta Exitosa!</h6>
                    <div class="small">Factura: ${result.data.numero_factura}</div>
                </div>
                <div class="fs-4 fw-bold">$${result.data.total_bruto.toFixed(2)}</div>
            </div>
        `;
        msgDiv.style.display = 'block';
        
        // Limpiar carrito y recargar productos (para actualizar stock)
        carrito = [];
        actualizarCarrito();
        document.getElementById('clienteNombre').value = '';
        loadProductos(document.getElementById('searchProducto').value, document.getElementById('categoriaVentaFilter').value);
        
        setTimeout(() => msgDiv.style.display = 'none', 5000);
        
    } catch (error) {
        msgDiv.className = 'alert alert-danger shadow-sm';
        msgDiv.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>Error: ${error.message}`;
        msgDiv.style.display = 'block';
        setTimeout(() => msgDiv.style.display = 'none', 5000);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Cobrar Venta';
    }
}