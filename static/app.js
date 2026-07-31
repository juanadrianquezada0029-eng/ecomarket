document.addEventListener("DOMContentLoaded", () => {
    const productoForm = document.getElementById("producto-form");
    const opinionForm = document.getElementById("opinion-form");
    const feedbackProducto = document.getElementById("producto-feedback");
    const feedbackOpinion = document.getElementById("opinion-feedback");
    const resultadoSentimiento = document.getElementById("resultado-sentimiento");
    const sentimientoText = document.getElementById("sentimiento-text");
    const resumenGrid = document.getElementById("resumen-grid");
    const productosList = document.getElementById("productos-list");
    const toggleForm = document.getElementById("toggle-form");
    const productoFormWrapper = document.getElementById("producto-form-wrapper");
    const productosCount = document.getElementById("productos-count");

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
            card.innerHTML = `<strong>${cantidad}</strong><p>${sentimiento.charAt(0).toUpperCase() + sentimiento.slice(1)}</p>`;
            resumenGrid.appendChild(card);
        });
    }

    toggleForm.addEventListener("click", () => {
        productoFormWrapper.scrollIntoView({ behavior: "smooth", block: "start" });
    });

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

            const nuevoProducto = document.createElement("article");
            nuevoProducto.classList.add("card-producto");
            nuevoProducto.innerHTML = `
                <div class="card-producto-top">
                    <h3>${result.producto.nombre}</h3>
                    <p class="precio">$${result.producto.precio.toFixed(2)}</p>
                </div>
                <span class="categoria"><i aria-hidden="true"></i>${result.producto.categoria}</span>
                <p class="descripcion">${result.producto.descripcion}</p>
            `;
            productosList.prepend(nuevoProducto);
            productosCount.textContent = Number(productosCount.textContent || 0) + 1;
        } catch (error) {
            setFeedback(feedbackProducto, error.message, "error");
        } finally {
            setLoading(submitBtn, false);
        }
    });

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
            resultadoSentimiento.dataset.sentimiento = result.sentimiento;
            resultadoSentimiento.hidden = false;

            renderResumen(result.resumen);
        } catch (error) {
            setFeedback(feedbackOpinion, error.message, "error");
        } finally {
            setLoading(submitBtn, false);
        }
    });
});
