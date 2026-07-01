document.addEventListener("DOMContentLoaded", () => {
    const orderForm = document.getElementById("orderForm");
    const typeSelect = document.getElementById("type");
    const priceGroup = document.getElementById("priceGroup");
    const stopPriceGroup = document.getElementById("stopPriceGroup");
    
    const priceInput = document.getElementById("price");
    const stopPriceInput = document.getElementById("stopPrice");
    
    const btnSubmit = document.getElementById("btnSubmit");
    const statusPlaceholder = document.getElementById("statusPlaceholder");
    const reportContainer = document.getElementById("reportContainer");
    const reportHeader = document.getElementById("reportHeader");
    const reportTitle = document.getElementById("reportTitle");
    
    const resOrderId = document.getElementById("resOrderId");
    const resStatus = document.getElementById("resStatus");
    const resQty = document.getElementById("resQty");
    const resPrice = document.getElementById("resPrice");
    const resTime = document.getElementById("resTime");
    
    const errorDetailsRow = document.getElementById("errorDetailsRow");
    const resError = document.getElementById("resError");
    
    const terminalBody = document.getElementById("terminalBody");
    const btnClearConsole = document.getElementById("btnClearConsole");

    // --- 1. Toggle Pricing Inputs Based on Order Type ---
    function updateFieldVisibilities() {
        const orderType = typeSelect.value;
        if (orderType === "MARKET") {
            priceGroup.classList.add("hidden");
            stopPriceGroup.classList.add("hidden");
            priceInput.removeAttribute("required");
            stopPriceInput.removeAttribute("required");
        } else if (orderType === "LIMIT") {
            priceGroup.classList.remove("hidden");
            stopPriceGroup.classList.add("hidden");
            priceInput.setAttribute("required", "true");
            stopPriceInput.removeAttribute("required");
        } else if (orderType === "STOP_LIMIT") {
            priceGroup.classList.remove("hidden");
            stopPriceGroup.classList.remove("hidden");
            priceInput.setAttribute("required", "true");
            stopPriceInput.setAttribute("required", "true");
        }
    }
    
    typeSelect.addEventListener("change", updateFieldVisibilities);
    updateFieldVisibilities(); // Initial trigger

    // --- 2. Order Submission Handling ---
    orderForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // Setup visual submission state
        btnSubmit.disabled = true;
        btnSubmit.textContent = "Transmitting... 📡";
        
        const symbol = document.getElementById("symbol").value.trim();
        const side = document.querySelector('input[name="side"]:checked').value;
        const type = typeSelect.value;
        const quantity = parseFloat(document.getElementById("quantity").value);
        const dryRun = document.getElementById("dryRun").checked;
        
        let price = null;
        if (type === "LIMIT" || type === "STOP_LIMIT") {
            price = parseFloat(priceInput.value);
        }
        
        let stopPrice = null;
        if (type === "STOP_LIMIT") {
            stopPrice = parseFloat(stopPriceInput.value);
        }
        
        const payload = {
            symbol,
            side,
            type,
            quantity,
            price,
            stop_price: stopPrice,
            dry_run: dryRun
        };

        try {
            const response = await fetch("/api/order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                displaySuccess(result);
            } else {
                displayFailure(result.detail || { error_type: "Network Error", message: "Failed to communicate with API server" });
            }
        } catch (error) {
            displayFailure({ error_type: "Connection Lost", message: error.message });
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.textContent = "Transmit Order ⚡";
            // Trigger log refresh immediately after submission
            fetchLogs();
        }
    });

    function displaySuccess(res) {
        statusPlaceholder.classList.add("hidden");
        reportContainer.classList.remove("hidden");
        
        reportHeader.className = "report-banner success";
        reportTitle.textContent = "✔ Order Successful";
        
        resOrderId.textContent = res.orderId || "N/A";
        resStatus.textContent = res.status || "N/A";
        resQty.textContent = res.executedQty || "0.00";
        resPrice.textContent = res.avgPrice || "0.00";
        
        // Parse update time
        if (res.updateTime) {
            const date = new Date(res.updateTime);
            resTime.textContent = date.toISOString().replace("T", " ").substring(0, 19) + " UTC";
        } else {
            resTime.textContent = "N/A";
        }
        
        errorDetailsRow.classList.add("hidden");
    }

    function displayFailure(errorDetail) {
        statusPlaceholder.classList.add("hidden");
        reportContainer.classList.remove("hidden");
        
        reportHeader.className = "report-banner error";
        reportTitle.textContent = "✘ Order Failed";
        
        resOrderId.textContent = "N/A";
        resStatus.textContent = errorDetail.error_type || "Error";
        resQty.textContent = "0.00";
        resPrice.textContent = "N/A";
        resTime.textContent = "N/A";
        
        errorDetailsRow.classList.remove("hidden");
        let detailText = errorDetail.message || "Unknown error";
        if (errorDetail.code !== undefined) {
            detailText += ` (Binance Code: ${errorDetail.code})`;
        }
        resError.textContent = detailText;
    }

    // --- 3. Live Logs Streaming via Polling ---
    function formatLogLine(rawLine) {
        // Match timestamps in brackets e.g. [2026-07-01 16:15:32]
        const dateRegex = /^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]/;
        const levelRegex = /\[(INFO|ERROR|WARNING)\]/;
        
        let formatted = rawLine;
        let tsSpan = "";
        let lvlSpan = "";
        
        const dateMatch = rawLine.match(dateRegex);
        if (dateMatch) {
            tsSpan = `<span class="timestamp">[${dateMatch[1]}]</span>`;
            formatted = formatted.replace(dateMatch[0], "");
        }
        
        const lvlMatch = formatted.match(levelRegex);
        if (lvlMatch) {
            const level = lvlMatch[1];
            const className = `level-${level.toLowerCase()}`;
            lvlSpan = `<span class="${className}">[${level}]</span>`;
            formatted = formatted.replace(lvlMatch[0], "");
        }
        
        return `<div class="log-line">${tsSpan}${lvlSpan}${escapeHtml(formatted)}</div>`;
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function fetchLogs() {
        try {
            const response = await fetch("/api/logs");
            const data = await response.json();
            
            if (data && Array.isArray(data.logs)) {
                const isScrolledToBottom = terminalBody.scrollHeight - terminalBody.clientHeight <= terminalBody.scrollTop + 30;
                
                terminalBody.innerHTML = data.logs
                    .map(line => formatLogLine(line))
                    .join("");
                
                if (isScrolledToBottom) {
                    terminalBody.scrollTop = terminalBody.scrollHeight;
                }
            }
        } catch (err) {
            console.error("Failed to fetch logs:", err);
        }
    }

    // Clear console button action
    btnClearConsole.addEventListener("click", () => {
        terminalBody.innerHTML = `<div class="log-line" style="color: var(--text-muted);">Console cleared by user.</div>`;
    });

    // Start polling logs every 3 seconds
    fetchLogs(); // Initial load
    setInterval(fetchLogs, 3000);
});
