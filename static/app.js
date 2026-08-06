document.addEventListener("DOMContentLoaded", () => {
    const productoForm = document.getElementById("producto-form");
    const opinionForm = document.getElementById("opinion-form");
    const feedbackProducto = document.getElementById("producto-feedback");
    const feedbackOpinion = document.getElementById("opinion-feedback");
    const resultadoSentimiento = document.getElementById("resultado-sentimiento");
    const sentimientoText = document.getElementById("sentimiento-text");
    const sentimientoEmoji = document.getElementById("sentimiento-emoji");
    const resumenGrid = document.getElementById("resumen-grid");
    const productosList = document.getElementById("productos-list");
    const toggleForm = document.getElementById("toggle-form");
    const productoFormWrapper = document.getElementById("producto-form-wrapper");
    const productosCount = document.getElementById("productos-count");

    // ---------- Utilidades ----------

    const EMOJIS_SENTIMIENTO = { positivo: "😊", negativo: "😞", neutral: "😐" };

    function escapeHTML(texto) {
        const div = document.createElement("div");
        div.textContent = texto ?? "";
        return div.innerHTML;
    }

    function formatMoney(valor) {
        return `$${Number(valor).toFixed(2)}`;
    }

    function setFeedback(el, message, tone) {
        el.textContent = message;
        el.classList.remove("is-success", "is-error");
        if (tone) el.classList.add(tone === "success" ? "is-success" : "is-error");
        el.classList.toggle("is-visible", Boolean(message));
    }

    function setLoading(button, loading) {
        button.classList.toggle("is-loading", loading);
        button.disabled = loading;
    }

    function renderResumen(resumen) {
        resumenGrid.innerHTML = "";
        resumen.forEach(([sentimiento, cantidad]) => {
            const card = document.createElement("div");
            card.className = "resumen-card";
            card.dataset.sentimiento = sentimiento;
            const emoji = EMOJIS_SENTIMIENTO[sentimiento] || "🙂";
            card.innerHTML = `
                <span class="resumen-emoji" aria-hidden="true">${emoji}</span>
                <strong>${cantidad}</strong>
                <p>${escapeHTML(sentimiento.charAt(0).toUpperCase() + sentimiento.slice(1))}</p>
            `;
            resumenGrid.appendChild(card);
        });
    }

    function crearTarjetaProducto(producto) {
        const article = document.createElement("article");
        article.className = "card-producto";
        article.dataset.id = producto.id;
        article.dataset.precio = producto.precio;
        article.innerHTML = `
            <button type="button" class="card-delete" data-action="eliminar" aria-label="Eliminar ${escapeHTML(producto.nombre)}" title="Eliminar producto">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2m2 0-.8 12.1a2 2 0 0 1-2 1.9H8.8a2 2 0 0 1-2-1.9L6 7" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
            <div class="card-producto-top">
                <h3>${escapeHTML(producto.nombre)}</h3>
                <p class="precio">${formatMoney(producto.precio)}</p>
            </div>
            <span class="categoria"><i aria-hidden="true"></i>${escapeHTML(producto.categoria)}</span>
            <p class="descripcion">${escapeHTML(producto.descripcion)}</p>
            <button type="button" class="btn btn-add-cart" data-action="agregar-carrito">Agregar al carrito</button>
        `;
        return article;
    }

    toggleForm.addEventListener("click", () => {
        productoFormWrapper.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    // ---------- Registrar producto ----------

    productoForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitBtn = productoForm.querySelector(".btn-submit");
        setLoading(submitBtn, true);
        setFeedback(feedbackProducto, "Guardando producto...", null);

        const formulario = new FormData(productoForm);
        const data = {
            nombre: formulario.get("nombre"),
            precio: formulario.get("precio"),
            categoria: formulario.get("categoria"),
            descripcion: formulario.get("descripcion"),
        };

        try {
            const response = await fetch("/api/productos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || "Error al crear el producto.");
            }

            setFeedback(feedbackProducto, "Producto agregado correctamente.", "success");
            productoForm.reset();

            productosList.prepend(crearTarjetaProducto(result.producto));
            productosCount.textContent = Number(productosCount.textContent || 0) + 1;
        } catch (error) {
            setFeedback(feedbackProducto, error.message, "error");
        } finally {
            setLoading(submitBtn, false);
        }
    });

    // ---------- Eliminar / agregar al carrito (delegación de eventos) ----------

    productosList.addEventListener("click", async (event) => {
        const deleteBtn = event.target.closest('[data-action="eliminar"]');
        const addBtn = event.target.closest('[data-action="agregar-carrito"]');

        if (deleteBtn) {
            const card = deleteBtn.closest(".card-producto");
            const id = card?.dataset.id;
            const nombre = card?.querySelector("h3")?.textContent || "este producto";
            if (!id) return;
            if (!window.confirm(`¿Eliminar "${nombre}" del catálogo? Esta acción no se puede deshacer.`)) {
                return;
            }
            deleteBtn.classList.add("is-loading");
            deleteBtn.disabled = true;
            try {
                const response = await fetch(`/api/productos/${id}`, { method: "DELETE" });
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || "No se pudo eliminar el producto.");
                }
                card.remove();
                productosCount.textContent = Math.max(0, Number(productosCount.textContent || 0) - 1);
                Carrito.quitar(id);
            } catch (error) {
                window.alert(error.message);
                deleteBtn.classList.remove("is-loading");
                deleteBtn.disabled = false;
            }
            return;
        }

        if (addBtn) {
            const card = addBtn.closest(".card-producto");
            if (!card) return;
            const producto = {
                id: card.dataset.id,
                nombre: card.querySelector("h3")?.textContent || "Producto",
                precio: parseFloat(card.dataset.precio) || 0,
            };
            Carrito.agregar(producto);
            addBtn.textContent = "Agregado ✓";
            addBtn.classList.add("is-added");
            setTimeout(() => {
                addBtn.textContent = "Agregar al carrito";
                addBtn.classList.remove("is-added");
            }, 1100);
        }
    });

    // ---------- Analizar opinión (emoción/sentimiento) ----------

    opinionForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitBtn = opinionForm.querySelector(".btn-submit");
        setLoading(submitBtn, true);
        setFeedback(feedbackOpinion, "Analizando opinión...", null);
        resultadoSentimiento.hidden = true;

        const texto = document.getElementById("texto-opinion").value;

        try {
            const response = await fetch("/api/analizar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ texto }),
            });
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || "Error al analizar la opinión.");
            }

            setFeedback(feedbackOpinion, "Análisis completado.", "success");
            sentimientoText.textContent = result.sentimiento;
            if (sentimientoEmoji) {
                sentimientoEmoji.textContent = EMOJIS_SENTIMIENTO[result.sentimiento] || "🙂";
            }
            resultadoSentimiento.dataset.sentimiento = result.sentimiento;
            resultadoSentimiento.hidden = false;

            renderResumen(result.resumen);
        } catch (error) {
            setFeedback(feedbackOpinion, error.message, "error");
        } finally {
            setLoading(submitBtn, false);
        }
    });

    // ---------- Carrito de compras (persistido en localStorage) ----------

    const Carrito = (() => {
        const STORAGE_KEY = "ecomarket_carrito";

        const toggleCartBtn = document.getElementById("toggle-cart");
        const closeCartBtn = document.getElementById("close-cart");
        const overlay = document.getElementById("cart-overlay");
        const drawer = document.getElementById("cart-drawer");
        const itemsBody = document.getElementById("cart-items");
        const emptyMsg = document.getElementById("cart-empty");
        const badge = document.getElementById("cart-badge");
        const totalEl = document.getElementById("cart-total");
        const checkoutBtn = document.getElementById("cart-checkout");
        const clearBtn = document.getElementById("cart-clear");

        function leer() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                return raw ? JSON.parse(raw) : [];
            } catch {
                return [];
            }
        }

        function guardar(items) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        }

        function agregar(producto) {
            const items = leer();
            const existente = items.find((item) => item.id === producto.id);
            if (existente) {
                existente.cantidad += 1;
            } else {
                items.push({ id: producto.id, nombre: producto.nombre, precio: producto.precio, cantidad: 1 });
            }
            guardar(items);
            render();
        }

        function cambiarCantidad(id, delta) {
            const items = leer();
            const item = items.find((i) => i.id === id);
            if (!item) return;
            item.cantidad += delta;
            const filtrados = item.cantidad <= 0 ? items.filter((i) => i.id !== id) : items;
            guardar(filtrados);
            render();
        }

        function quitar(id) {
            const items = leer().filter((item) => item.id !== id);
            guardar(items);
            render();
        }

        function vaciar() {
            guardar([]);
            render();
        }

        function render() {
            const items = leer();
            const totalItems = items.reduce((sum, item) => sum + item.cantidad, 0);
            const total = items.reduce((sum, item) => sum + item.cantidad * item.precio, 0);

            badge.textContent = totalItems;
            badge.hidden = totalItems === 0;
            totalEl.textContent = formatMoney(total);
            checkoutBtn.disabled = items.length === 0;

            itemsBody.innerHTML = "";
            if (items.length === 0) {
                itemsBody.appendChild(emptyMsg);
                emptyMsg.hidden = false;
                return;
            }
            emptyMsg.hidden = true;

            items.forEach((item) => {
                const row = document.createElement("div");
                row.className = "cart-item";
                row.innerHTML = `
                    <span class="cart-item-name">${escapeHTML(item.nombre)}</span>
                    <button type="button" class="cart-item-remove" data-id="${item.id}">Quitar</button>
                    <div class="cart-item-meta">
                        <div class="cart-item-qty">
                            <button type="button" data-id="${item.id}" data-delta="-1" aria-label="Restar unidad">&minus;</button>
                            <span>${item.cantidad}</span>
                            <button type="button" data-id="${item.id}" data-delta="1" aria-label="Sumar unidad">&plus;</button>
                        </div>
                        <span class="cart-item-subtotal">${formatMoney(item.cantidad * item.precio)}</span>
                    </div>
                `;
                itemsBody.appendChild(row);
            });
        }

        function abrir() {
            overlay.hidden = false;
            drawer.hidden = false;
            toggleCartBtn.setAttribute("aria-expanded", "true");
            document.body.style.overflow = "hidden";
        }

        function cerrar() {
            overlay.hidden = true;
            drawer.hidden = true;
            toggleCartBtn.setAttribute("aria-expanded", "false");
            document.body.style.overflow = "";
        }

        toggleCartBtn.addEventListener("click", abrir);
        closeCartBtn.addEventListener("click", cerrar);
        overlay.addEventListener("click", cerrar);
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !drawer.hidden) cerrar();
        });

        itemsBody.addEventListener("click", (event) => {
            const removeBtn = event.target.closest(".cart-item-remove");
            const qtyBtn = event.target.closest("[data-delta]");
            if (removeBtn) {
                quitar(removeBtn.dataset.id);
            } else if (qtyBtn) {
                cambiarCantidad(qtyBtn.dataset.id, Number(qtyBtn.dataset.delta));
            }
        });

        clearBtn.addEventListener("click", () => {
            if (leer().length === 0) return;
            if (window.confirm("¿Vaciar todo el carrito?")) vaciar();
        });

        checkoutBtn.addEventListener("click", () => {
            if (leer().length === 0) return;
            window.alert("¡Gracias por tu compra! (demo académica: no se procesan pagos reales)");
            vaciar();
            cerrar();
        });

        render();

        return { agregar, quitar, cambiarCantidad, vaciar };
    })();
});
