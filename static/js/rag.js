/* =========================================
   FITFLOW AI - ONLINE RAG COACH FRONTEND
   ========================================= */

document.addEventListener("DOMContentLoaded", () => {
    const ragForm = document.getElementById("ragCoachForm");
    const ragQueryInput = document.getElementById("ragQueryInput");
    const ragSubmitBtn = document.getElementById("ragSubmitBtn");
    const ragFocusSelect = document.getElementById("ragFocusFilter");
    const ragResultsBox = document.getElementById("ragResultsBox");
    const ragStatusBadge = document.getElementById("ragStatusBadge");
    const ragSafetyAlert = document.getElementById("ragSafetyAlert");
    const ragRetrievedGrid = document.getElementById("ragRetrievedGrid");
    const ragGeneratedBody = document.getElementById("ragGeneratedBody");
    const ragErrorBox = document.getElementById("ragErrorBox");
    const ragPromptChips = document.querySelectorAll(".rag-chip");

    if (!ragForm || !ragQueryInput || !ragSubmitBtn) {
        return;
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = String(str || "");
        return div.innerHTML;
    }

    function formatMarkdownToHtml(md) {
        const escaped = escapeHtml(md);
        const lines = escaped.split(/\r?\n/);
        const htmlLines = [];
        let inList = false;

        for (const rawLine of lines) {
            const line = rawLine.trim();
            if (!line) {
                if (inList) {
                    htmlLines.push("</ul>");
                    inList = false;
                }
                continue;
            }

            // Bold and inline citations
            let formatted = line
                .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
                .replace(/\[Doc\s+(\d+):\s*([^\]]+)\]/g, '<span class="rag-citation">[Doc $1: $2]</span>');

            if (formatted.startsWith("### ")) {
                if (inList) { htmlLines.push("</ul>"); inList = false; }
                htmlLines.push(`<h4 class="rag-md-h4">${formatted.slice(4)}</h4>`);
            } else if (formatted.startsWith("## ")) {
                if (inList) { htmlLines.push("</ul>"); inList = false; }
                htmlLines.push(`<h3 class="rag-md-h3">${formatted.slice(3)}</h3>`);
            } else if (/^[-*•]\s+/.test(formatted)) {
                if (!inList) { htmlLines.push('<ul class="rag-md-list">'); inList = true; }
                htmlLines.push(`<li>${formatted.replace(/^[-*•]\s+/, "")}</li>`);
            } else if (/^\d+\.\s+/.test(formatted)) {
                if (!inList) { htmlLines.push('<ul class="rag-md-list rag-md-ordered">'); inList = true; }
                htmlLines.push(`<li>${formatted}</li>`);
            } else {
                if (inList) { htmlLines.push("</ul>"); inList = false; }
                htmlLines.push(`<p class="rag-md-p">${formatted}</p>`);
            }
        }
        if (inList) htmlLines.push("</ul>");
        return htmlLines.join("");
    }

    function renderRetrievedDocs(docs) {
        if (!ragRetrievedGrid) return;
        if (!docs || !docs.length) {
            ragRetrievedGrid.innerHTML = '<p class="rag-empty">No matching source documents retrieved.</p>';
            return;
        }
        ragRetrievedGrid.innerHTML = docs.map((doc, idx) => {
            const meta = doc.metadata || {};
            const target = meta.target || meta.focus || meta.body_part || "General";
            const equip = meta.equipment || "Bodyweight";
            const typeLabel = String(doc.doc_type || "exercise").toUpperCase();
            return `
                <div class="rag-doc-card">
                    <div class="rag-doc-top">
                        <span class="rag-doc-badge rag-badge-${escapeHtml(doc.doc_type)}">Doc ${idx + 1} · ${escapeHtml(typeLabel)}</span>
                        <span class="rag-sim-score">${escapeHtml(doc.similarity_pct)}% match</span>
                    </div>
                    <h5 class="rag-doc-title">${escapeHtml(doc.title)}</h5>
                    <p class="rag-doc-meta">Target: <strong>${escapeHtml(target)}</strong> · ${escapeHtml(equip)}</p>
                    <span class="rag-doc-source">Source: ${escapeHtml(doc.source_file)}</span>
                </div>
            `;
        }).join("");
    }

    ragPromptChips.forEach((chip) => {
        chip.addEventListener("click", () => {
            const promptText = chip.getAttribute("data-prompt") || chip.textContent.trim();
            ragQueryInput.value = promptText;
            ragQueryInput.focus();
        });
    });

    ragForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = ragQueryInput.value.trim();
        if (!query) {
            ragQueryInput.focus();
            return;
        }

        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
        const focusFilter = ragFocusSelect ? ragFocusSelect.value : "all";

        ragSubmitBtn.disabled = true;
        ragSubmitBtn.textContent = "Retrieving & Generating...";
        if (ragErrorBox) {
            ragErrorBox.hidden = true;
            ragErrorBox.textContent = "";
        }
        if (ragSafetyAlert) {
            ragSafetyAlert.hidden = true;
            ragSafetyAlert.innerHTML = "";
        }

        try {
            const res = await fetch("/api/rag-coach", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                },
                body: JSON.stringify({
                    query,
                    focus_filter: focusFilter,
                    top_k: 5,
                }),
            });

            const data = await res.json();
            if (ragResultsBox) ragResultsBox.hidden = false;

            if (data.retrieved_documents && data.retrieved_documents.length) {
                renderRetrievedDocs(data.retrieved_documents);
            } else if (ragRetrievedGrid) {
                ragRetrievedGrid.innerHTML = "";
            }

            if (data.safety_warnings && data.safety_warnings.length && ragSafetyAlert) {
                ragSafetyAlert.hidden = false;
                ragSafetyAlert.innerHTML = `<strong>Clinical Safety Guardrail Active:</strong> ${data.safety_warnings.map(escapeHtml).join(" ")}`;
            }

            if (!res.ok || !data.success) {
                if (ragStatusBadge) ragStatusBadge.textContent = data.missing_api_key ? "Vector Retrieval Complete · Online API Key Required" : "Safety / Request Notice";
                if (ragGeneratedBody) ragGeneratedBody.innerHTML = "";
                if (ragErrorBox) {
                    ragErrorBox.hidden = false;
                    ragErrorBox.textContent = data.error || "Could not generate response.";
                }
                return;
            }

            if (ragStatusBadge) {
                ragStatusBadge.textContent = data.model_used || "Online RAG + ICL";
            }
            if (ragGeneratedBody) {
                ragGeneratedBody.innerHTML = formatMarkdownToHtml(data.answer);
            }
        } catch (err) {
            if (ragResultsBox) ragResultsBox.hidden = false;
            if (ragErrorBox) {
                ragErrorBox.hidden = false;
                ragErrorBox.textContent = "Network error while contacting the RAG Coach. Please try again.";
            }
        } finally {
            ragSubmitBtn.disabled = false;
            ragSubmitBtn.textContent = "Generate RAG Guidance ✦";
        }
    });
});


// Floating Yogi Coach smooth scroll & focus
document.addEventListener("DOMContentLoaded", () => {
    const yogiFab = document.getElementById("yogiCoachFab");
    const coachSection = document.getElementById("ai-coach");
    const ragInput = document.getElementById("ragQueryInput");
    if (yogiFab && coachSection) {
        yogiFab.addEventListener("click", (e) => {
            e.preventDefault();
            coachSection.scrollIntoView({ behavior: "smooth", block: "start" });
            if (ragInput) {
                setTimeout(() => ragInput.focus({ preventScroll: true }), 450);
            }
        });
    }
});
