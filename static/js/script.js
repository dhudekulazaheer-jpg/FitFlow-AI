
/* =========================================
   FITFLOW AI - COMPLETE FRONTEND
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================
       DOM ELEMENTS
    ===================================== */

    const planForm = document.getElementById("planForm");
    const generateBtn = document.getElementById("generateBtn");

    const resultsSection = document.getElementById("results");
    const planSummary = document.getElementById("planSummary");
    const planContent = document.getElementById("planContent");

    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    const sidebarOverlay = document.getElementById("sidebarOverlay");
    const closeSidebar = document.getElementById("closeSidebar");

    const utilitySection = document.getElementById("utilityViews");

    const utilityViews = {
        plans: document.getElementById("plansView"),
        history: document.getElementById("historyView"),
        bmi: document.getElementById("bmiView"),
        profile: document.getElementById("profileView")
    };

    const savedPlansContent = document.getElementById("savedPlansContent");
    const historyContent = document.getElementById("historyContent");

    const bmiForm = document.getElementById("bmiForm");
    const bmiResult = document.getElementById("bmiResult");

    const profileForm = document.getElementById("profileForm");
    const profileMessage = document.getElementById("profileMessage");


    /* =====================================
       BASIC VALIDATION
    ===================================== */

    if (
        !planForm ||
        !generateBtn ||
        !resultsSection ||
        !planSummary ||
        !planContent ||
        !menuToggle ||
        !sidebar ||
        !sidebarOverlay ||
        !utilitySection
    ) {
        console.error("FitFlow AI: Required HTML elements are missing.");
        return;
    }


    /* =====================================
       API HELPER
    ===================================== */

    async function apiRequest(url, options = {}) {

        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
        const method = (options.method || "GET").toUpperCase();

        if (csrfToken && method !== "GET" && method !== "HEAD") {
            options.headers = {
                ...(options.headers || {}),
                "X-CSRFToken": csrfToken
            };
        }

        const response = await fetch(url, options);

        let data;

        try {
            data = await response.json();
        } catch {
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok || data.success === false) {
            const error = new Error(
                data.error || data.message || "Something went wrong."
            );
            error.safetyData = data;
            error.status = response.status;
            throw error;
        }

        return data;
    }


    function showMessage(container, message, className = "empty-state") {

        container.replaceChildren();

        const messageElement = document.createElement("div");
        messageElement.className = className;
        messageElement.textContent = message;

        container.appendChild(messageElement);
    }


    /* =====================================
       SIDEBAR OPEN AND CLOSE
    ===================================== */

    function openSidebar() {

        sidebar.classList.add("open");
        menuToggle.classList.add("active");

        sidebarOverlay.hidden = false;

        sidebar.setAttribute("aria-hidden", "false");
        sidebar.inert = false;

        menuToggle.setAttribute("aria-expanded", "true");
        menuToggle.setAttribute("aria-label", "Close menu");

        document.body.classList.add("sidebar-open");

        closeSidebar.focus();
    }


    function hideSidebar() {

        sidebar.classList.remove("open");
        menuToggle.classList.remove("active");

        sidebarOverlay.hidden = true;

        sidebar.setAttribute("aria-hidden", "true");
        sidebar.inert = true;

        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Open menu");

        document.body.classList.remove("sidebar-open");
    }


    menuToggle.addEventListener("click", () => {

        if (sidebar.classList.contains("open")) {
            hideSidebar();
        } else {
            openSidebar();
        }

    });


    closeSidebar.addEventListener("click", hideSidebar);

    sidebarOverlay.addEventListener("click", hideSidebar);


    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape" &&
            sidebar.classList.contains("open")) {

            hideSidebar();
            menuToggle.focus();

        }

    });


    /* =====================================
       SWITCH BETWEEN MAIN AND UTILITY VIEWS
    ===================================== */

    function showUtilityView(viewName) {

        Object.values(utilityViews).forEach(view => {
            view.hidden = true;
        });

        const selectedView = utilityViews[viewName];

        if (!selectedView) {
            return;
        }

        utilitySection.hidden = false;
        selectedView.hidden = false;

        document.querySelectorAll(".sidebar-link").forEach(button => {

            button.classList.toggle(
                "active",
                button.dataset.view === viewName
            );

        });

        utilitySection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }


    function showMainPage(target = "home") {

        utilitySection.hidden = true;

        Object.values(utilityViews).forEach(view => {
            view.hidden = true;
        });

        document.querySelectorAll(".sidebar-link").forEach(button => {
            button.classList.remove("active");
        });

        const targetElement = document.getElementById(target);

        if (targetElement) {

            targetElement.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

    }


    document.querySelectorAll(".sidebar-link").forEach(button => {

        button.addEventListener("click", () => {

            const viewName = button.dataset.view;

            hideSidebar();

            showUtilityView(viewName);

            if (viewName === "plans") {
                loadSavedPlans();
            }

            if (viewName === "history") {
                loadHistory();
            }

            if (viewName === "bmi") {
                loadBMIProfileDetails();
            }

            if (viewName === "profile") {
                loadProfile();
            }

        });

    });


    /* =====================================
       NORMAL NAVIGATION
    ===================================== */

    document.querySelectorAll(
        '.nav-links a, .nav-button, .hero a[href="#planner"], .footer a'
    ).forEach(link => {

        link.addEventListener("click", () => {

            hideSidebar();

            const target = link.getAttribute("href");

            if (target && target.startsWith("#")) {
                showMainPage(target.substring(1));
            } else if (target === "/") {
                showMainPage("home");
            }

        });

    });


    /* =====================================
       HEALTH ASSESSMENT MODULE
    ===================================== */

    const healthHeaderToggle = document.getElementById("healthHeaderToggle");
    const healthAssessmentBody = document.getElementById("healthAssessmentBody");
    const healthToggleBadge = document.getElementById("healthToggleBadge");
    const surgeryYes = document.getElementById("surgeryYes");
    const surgeryNo = document.getElementById("surgeryNo");
    const surgeryDetailsBox = document.getElementById("surgeryDetailsBox");
    const saveAssessmentBtn = document.getElementById("saveAssessmentBtn");
    const healthSaveStatus = document.getElementById("healthSaveStatus");

    if (healthHeaderToggle && healthAssessmentBody) {
        function toggleAssessment(e) {
            if (e) e.preventDefault();
            const isHidden = healthAssessmentBody.style.display === "none";
            healthAssessmentBody.style.display = isHidden ? "block" : "none";
            if (healthToggleBadge) {
                healthToggleBadge.textContent = isHidden ? "Hide Assessment ▴" : "Show Assessment ▾";
            }
        }
        healthHeaderToggle.addEventListener("click", toggleAssessment);
        if (healthToggleBadge) {
            healthToggleBadge.addEventListener("click", (e) => {
                e.stopPropagation();
                toggleAssessment(e);
            });
        }
    }

    if (surgeryYes && surgeryNo && surgeryDetailsBox) {
        function toggleSurgeryDetails() {
            surgeryDetailsBox.style.display = surgeryYes.checked ? "block" : "none";
        }
        surgeryYes.addEventListener("change", toggleSurgeryDetails);
        surgeryNo.addEventListener("change", toggleSurgeryDetails);
    }

    function collectHealthAssessmentData() {
        const checkedConditions = Array.from(
            document.querySelectorAll('input[name="health_conditions"]:checked')
        ).map(cb => cb.value);

        const hasSurgery = document.getElementById("surgeryYes")?.checked === true;
        const affectedPart = document.getElementById("affected_body_part")?.value?.trim() || "";
        const surgeryDate = document.getElementById("surgery_date")?.value || "";
        const medicallyCleared = document.getElementById("clearanceYes")?.checked === true;
        const additionalInfo = document.getElementById("additional_information")?.value?.trim() || "";

        return {
            selected_conditions: checkedConditions,
            previous_surgery: hasSurgery,
            affected_body_part: affectedPart,
            surgery_date: surgeryDate,
            medically_cleared: medicallyCleared,
            additional_information: additionalInfo
        };
    }

    async function loadHealthAssessment() {
        try {
            const res = await apiRequest("/api/health-assessment");
            if (res.success && res.assessment) {
                const a = res.assessment;
                const conditions = a.selected_conditions || [];
                document.querySelectorAll('input[name="health_conditions"]').forEach(cb => {
                    cb.checked = conditions.includes(cb.value);
                });

                if (a.previous_surgery) {
                    if (surgeryYes) surgeryYes.checked = true;
                    if (surgeryDetailsBox) surgeryDetailsBox.style.display = "block";
                } else {
                    if (surgeryNo) surgeryNo.checked = true;
                    if (surgeryDetailsBox) surgeryDetailsBox.style.display = "none";
                }

                if (document.getElementById("affected_body_part")) {
                    document.getElementById("affected_body_part").value = a.affected_body_part || "";
                }
                if (document.getElementById("surgery_date")) {
                    document.getElementById("surgery_date").value = a.surgery_date || "";
                }
                if (a.medically_cleared) {
                    if (document.getElementById("clearanceYes")) document.getElementById("clearanceYes").checked = true;
                } else {
                    if (document.getElementById("clearanceNo")) document.getElementById("clearanceNo").checked = true;
                }
                if (document.getElementById("additional_information")) {
                    document.getElementById("additional_information").value = a.additional_information || "";
                }

                // If user already saved health assessment data, expand the section
                if (conditions.length > 0 || a.previous_surgery) {
                    if (healthAssessmentBody) healthAssessmentBody.style.display = "block";
                    if (healthToggleBadge) healthToggleBadge.textContent = "Hide Assessment ▴";
                }
            }
        } catch (e) {
            console.warn("Could not pre-load health assessment:", e);
        }
    }

    if (saveAssessmentBtn) {
        saveAssessmentBtn.addEventListener("click", async () => {
            const assessmentData = collectHealthAssessmentData();
            saveAssessmentBtn.disabled = true;
            if (healthSaveStatus) {
                healthSaveStatus.textContent = "Saving assessment...";
                healthSaveStatus.className = "health-status-text saving";
            }

            try {
                const res = await apiRequest("/api/health-assessment", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(assessmentData)
                });
                if (healthSaveStatus) {
                    healthSaveStatus.textContent = "✓ Assessment saved successfully!";
                    healthSaveStatus.className = "health-status-text success";
                    setTimeout(() => { healthSaveStatus.textContent = ""; }, 4000);
                }
            } catch (err) {
                if (healthSaveStatus) {
                    healthSaveStatus.textContent = err.message || "Failed to save assessment.";
                    healthSaveStatus.className = "health-status-text error";
                }
            } finally {
                saveAssessmentBtn.disabled = false;
            }
        });
    }

    loadHealthAssessment();


    /* =====================================
       PLAN FORM SUBMISSION
    ===================================== */

    planForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const formData = new FormData(planForm);

        const userData = {
            plan_type: formData.get("plan_type"),
            goal: formData.get("goal"),
            fitness_level: formData.get("fitness_level"),
            duration: Number(formData.get("duration")),
            equipment: formData.get("equipment"),
            body_part: formData.get("body_part") || null,
            health_assessment: collectHealthAssessmentData()
        };

        generateBtn.disabled = true;
        generateBtn.textContent = "Generating Your Plan... ✦";

        planContent.replaceChildren();
        planSummary.replaceChildren();

        utilitySection.hidden = true;
        resultsSection.hidden = false;

        planSummary.textContent =
            "Preparing your personalized fitness routine...";

        resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        try {

            const result = await apiRequest("/api/generate-plan", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData)
            });

            renderPlan(result);

        } catch (error) {

            console.error("FitFlow AI Error:", error);

            planSummary.replaceChildren();

            if (error.safetyData && (error.safetyData.health_safety_paused || error.safetyData.paused)) {
                const pauseCard = document.createElement("div");
                pauseCard.className = "safety-paused-card";

                const pauseHeading = document.createElement("h3");
                pauseHeading.textContent = "⚠️ Exercise Safety Notice: Plan Generation Paused";

                const pauseText = document.createElement("p");
                pauseText.className = "pause-message";
                pauseText.textContent = error.safetyData.error || error.message;

                const guidanceBox = document.createElement("div");
                guidanceBox.className = "pause-guidance";
                guidanceBox.innerHTML = "<strong>Important Guidance:</strong> Because you reported a prior surgical procedure without confirmed medical clearance to exercise, FitFlow AI has paused routine generation. For your health and safety, please consult a qualified physician or healthcare professional to receive medical clearance before starting an exercise routine.";

                pauseCard.append(pauseHeading, pauseText, guidanceBox);
                planContent.replaceChildren(pauseCard);

            } else {

                const errorBox = document.createElement("div");
                errorBox.className = "error-message";
                errorBox.textContent =
                    error.message || "Unable to generate your plan.";

                planContent.replaceChildren(errorBox);

            }

        } finally {

            generateBtn.disabled = false;
            generateBtn.textContent = "Generate My Fitness Plan ✦";

        }

    });


    /* =====================================
       DISPLAY GENERATED PLAN
    ===================================== */

    function renderPlan(result) {

        planSummary.replaceChildren();
        planContent.replaceChildren();

        const heading = document.createElement("h3");
        heading.textContent = "Your personalized routine is ready!";

        currentActivePlanId = result.plan_id || null;
        currentActivePlan = result;

        const details = document.createElement("p");

        details.textContent =
            `Goal: ${formatText(result.goal || "—")} | ` +
            `Level: ${formatText(result.fitness_level || "—")} | ` +
            `Duration: ${result.requested_duration_minutes ?? "—"} minutes`;

        planSummary.append(heading, details);

        // Add Interactive Session Player Button
        const sessionExercises = extractSessionExercises(result);
        if (sessionExercises.length > 0) {
            const startBtn = document.createElement("button");
            startBtn.type = "button";
            startBtn.className = "start-session-btn";
            startBtn.innerHTML = "<span>▶</span> Start Interactive Session";
            startBtn.addEventListener("click", () => {
                launchInteractiveSession(sessionExercises, result);
            });
            planSummary.appendChild(startBtn);
        }

        // Render Safety Warnings if any
        if (result.safety_warnings && Array.isArray(result.safety_warnings) && result.safety_warnings.length > 0) {
            const warningBox = document.createElement("div");
            warningBox.className = "safety-warning-banner";

            const warnHeading = document.createElement("h4");
            warnHeading.innerHTML = "<span>⚠️</span> Health &amp; Movement Precautions";
            warningBox.appendChild(warnHeading);

            const warnList = document.createElement("ul");
            warnList.className = "safety-warning-list";
            result.safety_warnings.forEach(w => {
                const li = document.createElement("li");
                li.textContent = w;
                warnList.appendChild(li);
            });
            warningBox.appendChild(warnList);
            planContent.appendChild(warningBox);
        }

        const components = [
            { title: "Yoga Routine", key: "yoga", fallbackKey: "yoga_plan" },
            { title: "Workout Routine", key: "workout", fallbackKey: "workout_plan" }
        ];

        let displayed = false;

        components.forEach(component => {

            const plan = result[component.key] || result[component.fallbackKey];

            if (plan && typeof plan === "object") {

                renderSection(component.title, plan);
                displayed = true;

            }

        });

        if (!displayed) {
            renderSection("Your Fitness Routine", result);
        }

        // Render Post-Workout Recovery Nutrition Guide (Feature 6)
        if (result.recovery_nutrition) {
            renderRecoveryNutrition(result.recovery_nutrition);
        }

        // Render Medical Disclaimer if present
        if (result.disclaimer) {
            const disclaimerBox = document.createElement("div");
            disclaimerBox.className = "safety-disclaimer-note";
            disclaimerBox.textContent = `✦ Disclaimer: ${result.disclaimer}`;
            planContent.appendChild(disclaimerBox);
        }

        resultsSection.hidden = false;

    }


    function renderSection(title, data) {

        const section = document.createElement("div");
        section.className = "plan-card";

        const heading = document.createElement("h3");
        heading.textContent = title;

        section.appendChild(heading);

        renderValue(data, section, {
            isYoga: title.toLowerCase().includes("yoga")
        });

        planContent.appendChild(section);

    }


    /* =====================================
       FEATURE 6: RECOVERY NUTRITION RENDERER (Clean Editorial Layout)
    ===================================== */

    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function renderRecoveryNutrition(nutrition) {
        if (!nutrition) return;

        const card = document.createElement("div");
        card.className = "recovery-nutrition-card";

        // Editorial Header - No generic colored boxes
        const header = document.createElement("div");
        header.className = "recovery-editorial-header";
        header.innerHTML = `
            <span class="recovery-kicker">✦ Post-Workout Recovery Protocol</span>
            <h3 class="recovery-editorial-title">Nutrition &amp; Cellular Recovery</h3>
            <p class="recovery-editorial-subtitle">Optimal recovery window: Consume whole nourishment within 30–60 minutes to replenish depleted glycogen and accelerate cellular repair.</p>
        `;
        card.appendChild(header);

        // Typographic Metric Strip with Hairline Dividers (Zero chunky beige boxes)
        const strip = document.createElement("div");
        strip.className = "recovery-metrics-strip";
        strip.innerHTML = `
            <div class="recovery-stat-col">
                <div class="recovery-stat-number">${escapeHtml(nutrition.target_water_ml)}<span class="recovery-stat-unit">ml</span></div>
                <div class="recovery-stat-label">Hydration Target</div>
            </div>
            <div class="recovery-stat-col recovery-stat-divider">
                <div class="recovery-stat-number">${escapeHtml(nutrition.target_protein_g)}<span class="recovery-stat-unit">g</span></div>
                <div class="recovery-stat-label">Recovery Protein</div>
            </div>
            <div class="recovery-stat-col">
                <div class="recovery-stat-number recovery-stat-text">${escapeHtml(nutrition.carb_ratio || "Balanced 2:1")}</div>
                <div class="recovery-stat-label">Replenishment Profile</div>
            </div>
        `;
        card.appendChild(strip);

        // Curated Whole-Food Replenishment (Menu / Editorial List format instead of stacked beige pills)
        if (nutrition.recommended_snacks && nutrition.recommended_snacks.length > 0) {
            const snacksSec = document.createElement("div");
            snacksSec.className = "recovery-culinary-section";

            const snacksTitle = document.createElement("h4");
            snacksTitle.className = "recovery-culinary-title";
            snacksTitle.textContent = "Curated Whole-Food Replenishment";
            snacksSec.appendChild(snacksTitle);

            const snacksList = document.createElement("div");
            snacksList.className = "recovery-culinary-list";

            nutrition.recommended_snacks.forEach(s => {
                const row = document.createElement("div");
                row.className = "recovery-culinary-row";
                row.innerHTML = `
                    <div class="culinary-bullet">✦</div>
                    <div class="culinary-content">
                        <strong class="culinary-name">${escapeHtml(s.title)}</strong>
                        <span class="culinary-desc">${escapeHtml(s.detail)}</span>
                    </div>
                `;
                snacksList.appendChild(row);
            });

            snacksSec.appendChild(snacksList);
            card.appendChild(snacksSec);
        }

        // Editorial Footnote Note (Subtle, elegant italics instead of generic amber alert box)
        if (nutrition.electrolyte_tip) {
            const tip = document.createElement("div");
            tip.className = "recovery-editorial-footnote";
            tip.innerHTML = `
                <span class="footnote-mark">✦</span>
                <p><strong>Hydration Guidance:</strong> ${escapeHtml(nutrition.electrolyte_tip)}</p>
            `;
            card.appendChild(tip);
        }

        planContent.appendChild(card);
    }


    /* =====================================
       FEATURE 1: INTERACTIVE SESSION ENGINE
    ===================================== */

    let currentActivePlanId = null;
    let currentActivePlan = null;
    let sessionTimerInterval = null;
    let sessionStepIndex = 0;
    let sessionExercises = [];
    let sessionIsPaused = false;
    let sessionSecondsLeft = 45;

    function extractSessionExercises(planObj) {
        const exercises = [];
        function recurse(obj, isYoga) {
            if (!obj) return;
            if (Array.isArray(obj)) {
                obj.forEach(item => recurse(item, isYoga));
            } else if (typeof obj === "object") {
                if (obj.name && typeof obj.name === "string") {
                    exercises.push({
                        name: obj.name,
                        sub: obj.sanskrit_name || obj.target || (isYoga ? "Yoga Pose" : "Workout Movement"),
                        category: obj.category || obj.bodyPart || (isYoga ? "Flexibility" : "Strength"),
                        instructions: obj.instructions || obj.description || "Perform with controlled tempo and mindful breathing.",
                        isYoga: isYoga,
                        duration: isYoga ? 60 : 45
                    });
                } else {
                    Object.entries(obj).forEach(([k, v]) => {
                        const yogaFlag = isYoga || k.toLowerCase().includes("yoga");
                        recurse(v, yogaFlag);
                    });
                }
            }
        }
        recurse(planObj, false);
        return exercises;
    }

    function speakText(text) {
        const voiceToggle = document.getElementById("sessionVoiceToggle");
        if (voiceToggle && !voiceToggle.checked) return;
        if (!("speechSynthesis" in window)) return;
        try {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.warn("SpeechSynthesis error:", e);
        }
    }

    function launchInteractiveSession(exercises, planObj) {
        if (!exercises || exercises.length === 0) return;
        sessionExercises = exercises;
        sessionStepIndex = 0;
        sessionIsPaused = false;

        const sessionModal = document.getElementById("sessionModal");
        if (!sessionModal) return;

        sessionModal.hidden = false;
        document.body.classList.add("sidebar-open");

        const sessionTypeBadge = document.getElementById("sessionTypeBadge");
        const sessionRoutineTitle = document.getElementById("sessionRoutineTitle");
        if (sessionTypeBadge) {
            sessionTypeBadge.textContent = `${planObj.plan_type || "FITNESS"} • ${planObj.requested_duration_minutes || 30} MIN`;
        }
        if (sessionRoutineTitle) {
            sessionRoutineTitle.textContent = `${formatText(planObj.goal || "Fitness")} Session`;
        }

        renderCurrentSessionStep();
    }

    function renderCurrentSessionStep() {
        clearInterval(sessionTimerInterval);

        if (sessionStepIndex >= sessionExercises.length) {
            finishSession();
            return;
        }

        const step = sessionExercises[sessionStepIndex];
        sessionSecondsLeft = step.duration || 45;

        const sessionProgressBar = document.getElementById("sessionProgressBar");
        const sessionStepCounter = document.getElementById("sessionStepCounter");
        const sessionStepCategory = document.getElementById("sessionStepCategory");
        const sessionExerciseName = document.getElementById("sessionExerciseName");
        const sessionExerciseSub = document.getElementById("sessionExerciseSub");
        const sessionExerciseInstructions = document.getElementById("sessionExerciseInstructions");
        const sessionPlayPauseBtn = document.getElementById("sessionPlayPauseBtn");

        const pct = Math.round(((sessionStepIndex) / sessionExercises.length) * 100);
        if (sessionProgressBar) sessionProgressBar.style.width = `${pct}%`;
        if (sessionStepCounter) sessionStepCounter.textContent = `Exercise ${sessionStepIndex + 1} of ${sessionExercises.length}`;
        if (sessionStepCategory) sessionStepCategory.textContent = formatText(step.category);
        if (sessionExerciseName) sessionExerciseName.textContent = step.name;
        if (sessionExerciseSub) sessionExerciseSub.textContent = step.sub;
        if (sessionExerciseInstructions) sessionExerciseInstructions.textContent = step.instructions;
        if (sessionPlayPauseBtn) sessionPlayPauseBtn.textContent = "⏸ Pause";

        updateTimerDisplay();
        speakText(`Next: ${step.name}`);

        sessionIsPaused = false;
        sessionTimerInterval = setInterval(() => {
            if (sessionIsPaused) return;
            sessionSecondsLeft--;
            updateTimerDisplay();

            if (sessionSecondsLeft === 3) speakText("Three");
            if (sessionSecondsLeft === 2) speakText("Two");
            if (sessionSecondsLeft === 1) speakText("One");

            if (sessionSecondsLeft <= 0) {
                clearInterval(sessionTimerInterval);
                sessionStepIndex++;
                renderCurrentSessionStep();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        const sessionTimer = document.getElementById("sessionTimer");
        if (!sessionTimer) return;
        const mins = Math.floor(sessionSecondsLeft / 60);
        const secs = sessionSecondsLeft % 60;
        sessionTimer.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    async function finishSession() {
        clearInterval(sessionTimerInterval);
        const sessionProgressBar = document.getElementById("sessionProgressBar");
        if (sessionProgressBar) sessionProgressBar.style.width = "100%";

        const sessionExerciseName = document.getElementById("sessionExerciseName");
        const sessionExerciseSub = document.getElementById("sessionExerciseSub");
        const sessionTimer = document.getElementById("sessionTimer");
        const sessionExerciseInstructions = document.getElementById("sessionExerciseInstructions");
        const sessionControls = document.querySelector(".session-controls");

        if (sessionExerciseName) sessionExerciseName.textContent = "🎉 Session Completed!";
        if (sessionExerciseSub) sessionExerciseSub.textContent = "Outstanding effort! Your body and mind thank you.";
        if (sessionTimer) sessionTimer.textContent = "DONE";
        if (sessionExerciseInstructions) {
            sessionExerciseInstructions.textContent = "You've successfully finished all exercises in this routine. Progress has been logged to your activity history.";
        }
        if (sessionControls) {
            sessionControls.innerHTML = `<button type="button" class="session-btn session-btn-primary" id="finishCloseBtn">Close & View Progress ✦</button>`;
            document.getElementById("finishCloseBtn")?.addEventListener("click", closeSessionModal);
        }

        speakText("Session completed! Fantastic workout.");

        try {
            await apiRequest("/api/complete-session", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    plan_id: currentActivePlanId,
                    routine_name: currentActivePlan?.plan_type || "Routine",
                    duration: currentActivePlan?.requested_duration_minutes || 30
                })
            });
        } catch (e) {
            console.warn("Could not log completed session:", e);
        }
    }

    function closeSessionModal() {
        clearInterval(sessionTimerInterval);
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
        }
        const sessionModal = document.getElementById("sessionModal");
        if (sessionModal) sessionModal.hidden = true;
        document.body.classList.remove("sidebar-open");
    }

    // Modal listeners
    document.getElementById("closeSessionBtn")?.addEventListener("click", closeSessionModal);

    document.getElementById("sessionPlayPauseBtn")?.addEventListener("click", () => {
        sessionIsPaused = !sessionIsPaused;
        const btn = document.getElementById("sessionPlayPauseBtn");
        if (btn) btn.textContent = sessionIsPaused ? "▶ Resume" : "⏸ Pause";
    });

    document.getElementById("sessionNextBtn")?.addEventListener("click", () => {
        clearInterval(sessionTimerInterval);
        sessionStepIndex++;
        renderCurrentSessionStep();
    });

    document.getElementById("sessionPrevBtn")?.addEventListener("click", () => {
        if (sessionStepIndex > 0) {
            clearInterval(sessionTimerInterval);
            sessionStepIndex--;
            renderCurrentSessionStep();
        }
    });


    /* =====================================
       FEATURE 4: ANALYTICS & BADGES ENGINE
    ===================================== */

    let cachedAnalyticsData = null;
    let streakCalCurrentDate = new Date();

    async function loadAnalytics() {
        try {
            const res = await apiRequest("/api/analytics");
            if (res.success && res.analytics) {
                const a = res.analytics;
                cachedAnalyticsData = a;

                // Update Navbar Streak Count
                const navStreakCount = document.getElementById("navStreakCount");
                if (navStreakCount) {
                    navStreakCount.textContent = a.current_streak || 0;
                }

                const statStreak = document.getElementById("statStreak");
                const statCalories = document.getElementById("statCalories");
                const statCompleted = document.getElementById("statCompleted");
                const statPlans = document.getElementById("statPlans");
                const badgesGrid = document.getElementById("badgesGrid");

                if (statStreak) statStreak.textContent = a.current_streak;
                if (statCalories) statCalories.textContent = a.total_calories_burned;
                if (statCompleted) statCompleted.textContent = a.completed_sessions;
                if (statPlans) statPlans.textContent = a.total_plans;

                if (badgesGrid && Array.isArray(a.badges)) {
                    badgesGrid.replaceChildren();
                    a.badges.forEach(b => {
                        const badgeEl = document.createElement("div");
                        badgeEl.className = `badge-chip ${b.unlocked ? "unlocked" : "locked"}`;
                        badgeEl.innerHTML = `
                            <span class="badge-chip-icon">${b.icon}</span>
                            <div class="badge-chip-info">
                                <strong>${b.name}</strong>
                                <small>${b.description}</small>
                                <span class="badge-status-tag">${b.unlocked ? "✓ Unlocked" : "Locked"}</span>
                            </div>
                        `;
                        badgesGrid.appendChild(badgeEl);
                    });
                }
            }
        } catch (e) {
            console.warn("Analytics error:", e);
        }
    }


    /* =====================================
       FEATURE: STREAK & CONSISTENCY CALENDAR
    ===================================== */

    function openStreakCalendar() {
        const modal = document.getElementById("streakCalendarModal");
        if (!modal) return;

        const a = cachedAnalyticsData || { current_streak: 0, best_streak: 0, completed_sessions: 0, active_dates: [] };

        const calStreakVal = document.getElementById("calStreakVal");
        const calActiveStreak = document.getElementById("calActiveStreak");
        const calBestStreak = document.getElementById("calBestStreak");
        const calTotalSessions = document.getElementById("calTotalSessions");
        const calStreakSubtitle = document.getElementById("calStreakSubtitle");

        if (calStreakVal) calStreakVal.textContent = a.current_streak || 0;
        if (calActiveStreak) calActiveStreak.textContent = a.current_streak || 0;
        if (calBestStreak) calBestStreak.textContent = a.best_streak || a.current_streak || 0;
        if (calTotalSessions) calTotalSessions.textContent = a.completed_sessions || 0;

        if (calStreakSubtitle) {
            const streak = a.current_streak || 0;
            if (streak === 0) {
                calStreakSubtitle.textContent = "Start your streak today by completing your first workout or yoga routine!";
            } else if (streak === 1) {
                calStreakSubtitle.textContent = "Great start! Complete tomorrow's routine to build continuous momentum.";
            } else if (streak < 3) {
                calStreakSubtitle.textContent = "You're building strong momentum! Keep the fire burning.";
            } else {
                calStreakSubtitle.textContent = "You're on fire! Consistency is transforming your strength and vitality.";
            }
        }

        streakCalCurrentDate = new Date();
        renderStreakCalendar(streakCalCurrentDate, a.active_dates || []);

        modal.hidden = false;
        document.body.classList.add("sidebar-open");
    }

    function closeStreakCalendar() {
        const modal = document.getElementById("streakCalendarModal");
        if (modal) {
            modal.hidden = true;
            document.body.classList.remove("sidebar-open");
        }
    }

    function renderStreakCalendar(viewDate, activeDatesList) {
        const grid = document.getElementById("streakDaysGrid");
        const monthDisplay = document.getElementById("calMonthDisplay");
        if (!grid || !monthDisplay) return;

        grid.replaceChildren();

        const year = viewDate.getFullYear();
        const month = viewDate.getMonth();

        const monthNames = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        monthDisplay.textContent = `${monthNames[month]} ${year}`;

        const activeSet = new Set(activeDatesList || []);

        const now = new Date();
        const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

        const firstDay = new Date(year, month, 1).getDay();
        const startOffset = (firstDay + 6) % 7; // Mon = 0 ... Sun = 6
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        for (let i = 0; i < startOffset; i++) {
            const emptyCell = document.createElement("div");
            emptyCell.className = "streak-day empty-day";
            grid.appendChild(emptyCell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const cellDate = new Date(year, month, day);

            const dayCell = document.createElement("div");
            dayCell.className = "streak-day";

            const numSpan = document.createElement("span");
            numSpan.textContent = day;
            dayCell.appendChild(numSpan);

            const isActive = activeSet.has(dateStr);
            const isToday = dateStr === todayStr;
            const isFuture = cellDate > now && !isToday;

            if (isActive) {
                dayCell.classList.add("active-day");
                dayCell.title = `Workout session completed on ${dateStr}`;
                const check = document.createElement("span");
                check.className = "day-check";
                check.textContent = "✓";
                dayCell.appendChild(check);
            } else if (isFuture) {
                dayCell.classList.add("future-day");
            }

            if (isToday) {
                dayCell.classList.add("today-day");
                dayCell.title = isActive ? "Today - Routine Completed!" : "Today - Log a session to keep your streak!";
            }

            grid.appendChild(dayCell);
        }
    }

    document.getElementById("navStreakBtn")?.addEventListener("click", () => {
        loadAnalytics().then(() => openStreakCalendar());
    });

    document.getElementById("closeStreakModalBtn")?.addEventListener("click", closeStreakCalendar);

    document.getElementById("streakCalendarModal")?.addEventListener("click", (e) => {
        if (e.target.id === "streakCalendarModal") {
            closeStreakCalendar();
        }
    });

    document.getElementById("calPrevMonthBtn")?.addEventListener("click", () => {
        streakCalCurrentDate.setMonth(streakCalCurrentDate.getMonth() - 1);
        const a = cachedAnalyticsData || {};
        renderStreakCalendar(streakCalCurrentDate, a.active_dates || []);
    });

    document.getElementById("calNextMonthBtn")?.addEventListener("click", () => {
        streakCalCurrentDate.setMonth(streakCalCurrentDate.getMonth() + 1);
        const a = cachedAnalyticsData || {};
        renderStreakCalendar(streakCalCurrentDate, a.active_dates || []);
    });


    /* =====================================
       YOUTUBE REFERENCE LINKS
    ===================================== */

    function createYouTubeLink(name, isYoga) {

        const link = document.createElement("a");

        const searchText = isYoga
            ? `${name} yoga pose tutorial`
            : `${name} exercise demonstration`;

        link.href =
            "https://www.youtube.com/results?search_query=" +
            encodeURIComponent(searchText);

        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.className = "reference-link";
        link.textContent = "▶ Watch on YouTube";

        return link;

    }


    /* =====================================
       RECURSIVE PLAN DATA RENDERER
    ===================================== */

    function renderValue(data, container, context = {}) {

        if (data === null || data === undefined) {
            return;
        }

        if (Array.isArray(data)) {

            const list = document.createElement("ul");

            data.forEach(item => {

                const listItem = document.createElement("li");

                if (typeof item === "object" && item !== null) {
                    renderValue(item, listItem, context);
                } else {
                    listItem.textContent = formatText(item);
                }

                list.appendChild(listItem);

            });

            container.appendChild(list);
            return;
        }

        if (typeof data === "object") {

            const itemName = data.name || "";
            const isYoga = context.isYoga === true;

            Object.entries(data).forEach(([key, value]) => {

                if (
                    value === null ||
                    value === undefined ||
                    key === "success"
                ) {
                    return;
                }

                const normalizedKey = key.toLowerCase();

                // Exercise or yoga pose name
                if (
                    normalizedKey === "name" &&
                    typeof value === "string"
                ) {

                    const paragraph = document.createElement("p");

                    const label = document.createElement("strong");
                    label.textContent = "Name: ";

                    const name = document.createElement("span");
                    name.textContent = formatText(value);

                    paragraph.append(label, name);

                    if (itemName) {
                        paragraph.appendChild(
                            createYouTubeLink(itemName, isYoga)
                        );

                        // Smart Exercise Swap Button (Feature 5)
                        const swapBtn = document.createElement("button");
                        swapBtn.type = "button";
                        swapBtn.className = "exercise-swap-btn";
                        swapBtn.innerHTML = "<span>⇄</span> Swap";
                        swapBtn.title = "Find an alternative exercise / pose";
                        swapBtn.addEventListener("click", async (e) => {
                            e.preventDefault();
                            swapBtn.disabled = true;
                            swapBtn.textContent = "Swapping...";
                            try {
                                const swapRes = await apiRequest("/api/swap-exercise", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({
                                        plan_id: currentActivePlanId,
                                        current_name: itemName,
                                        is_yoga: isYoga,
                                        category: data.category || data.category_name,
                                        body_part: data.bodyPart || data.body_part,
                                        target: data.target
                                    })
                                });
                                if (swapRes.success && swapRes.new_exercise) {
                                    name.textContent = formatText(swapRes.new_exercise.name);
                                    swapBtn.textContent = "✓ Swapped";
                                    setTimeout(() => {
                                        swapBtn.innerHTML = "<span>⇄</span> Swap";
                                        swapBtn.disabled = false;
                                    }, 2000);
                                }
                            } catch (err) {
                                console.error("Swap failed:", err);
                                swapBtn.innerHTML = "<span>⇄</span> Swap";
                                swapBtn.disabled = false;
                            }
                        });
                        paragraph.appendChild(swapBtn);
                    }

                    container.appendChild(paragraph);
                    return;
                }


                // Yoga images and SVG references
                if (
                    typeof value === "string" &&
                    ["image", "svg", "image_url"].includes(normalizedKey)
                ) {

                    if (
                        !value.startsWith("https://") &&
                        !value.startsWith("http://")
                    ) {
                        return;
                    }

                    const mediaBox = document.createElement("div");
                    mediaBox.className = "reference-media";

                    const link = document.createElement("a");

                    link.href = value;
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                    link.className = "reference-link";

                    link.textContent =
                        normalizedKey === "svg"
                            ? "View SVG Reference"
                            : "View Pose Image";

                    mediaBox.appendChild(link);

                    if (normalizedKey !== "svg") {

                        const image = document.createElement("img");

                        image.src = value;
                        image.alt = "Yoga pose demonstration";
                        image.loading = "lazy";

                        image.onerror = () => image.remove();

                        mediaBox.appendChild(image);

                    }

                    container.appendChild(mediaBox);
                    return;
                }


                // Ignore broken local workout media
                if (
                    ["gif_url", "video_url"].includes(normalizedKey)
                ) {
                    return;
                }


                // Nested objects and arrays
                if (typeof value === "object") {

                    const nested = document.createElement("div");
                    nested.className = "plan-item";

                    const label = document.createElement("strong");
                    label.textContent = formatText(key);

                    nested.appendChild(label);

                    renderValue(value, nested, context);

                    container.appendChild(nested);
                    return;
                }


                // Normal text values
                const paragraph = document.createElement("p");

                const label = document.createElement("strong");
                label.textContent = `${formatText(key)}: `;

                const content = document.createElement("span");
                content.textContent = formatText(value);

                paragraph.append(label, content);

                container.appendChild(paragraph);

            });

            return;
        }


        const paragraph = document.createElement("p");
        paragraph.textContent = formatText(data);

        container.appendChild(paragraph);

    }


    /* =====================================
       TEXT FORMATTING
    ===================================== */

    function formatText(value) {

        if (typeof value === "string") {

            return value
                .replace(/_/g, " ")
                .replace(/\b\w/g, letter => letter.toUpperCase());

        }

        return String(value);

    }


    /* =====================================
       PREVIOUSLY GENERATED PLANS
    ===================================== */

    async function loadSavedPlans() {

        showMessage(savedPlansContent, "Loading your saved plans...", "loading-message");

        try {

            const response = await apiRequest("/api/plans");

            const plans = response.plans || [];

            savedPlansContent.replaceChildren();

            if (plans.length === 0) {

                showMessage(
                    savedPlansContent,
                    "You haven't generated any plans yet. Create your first fitness plan!"
                );

                return;
            }

            plans.forEach(plan => {

                const card = document.createElement("div");
                card.className = "saved-plan-card";

                const heading = document.createElement("h3");

                heading.textContent =
                    `${formatText(plan.plan_type || "Fitness")} Plan`;

                const goal = document.createElement("p");
                goal.textContent =
                    `Goal: ${formatText(plan.goal || "—")}`;

                const level = document.createElement("p");
                level.textContent =
                    `Level: ${formatText(plan.fitness_level || "—")}`;

                const duration = document.createElement("p");
                duration.textContent =
                    `Duration: ${plan.duration ?? "—"} minutes`;

                const date = document.createElement("p");
                date.textContent =
                    `Generated: ${formatDate(plan.generated_at)}`;

                const openButton = document.createElement("button");
                openButton.type = "button";
                openButton.textContent = "View This Plan";

                openButton.addEventListener("click", () => {
                    openSavedPlan(plan.id);
                });

                card.append(
                    heading,
                    goal,
                    level,
                    duration,
                    date,
                    openButton
                );

                savedPlansContent.appendChild(card);

            });

        } catch (error) {

            console.error("Saved plans error:", error);

            showMessage(
                savedPlansContent,
                error.message || "Unable to load saved plans."
            );

        }

    }


    /* =====================================
       OPEN A SAVED PLAN
    ===================================== */

    async function openSavedPlan(planId) {

        try {

            const response = await apiRequest(
                `/api/plans/${encodeURIComponent(planId)}`
            );

            const savedRecord = response.plan;

            if (!savedRecord || !savedRecord.plan) {
                throw new Error("Saved plan data is unavailable.");
            }

            utilitySection.hidden = true;

            resultsSection.hidden = false;

            renderPlan(savedRecord.plan);

            resultsSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {

            console.error("Open saved plan error:", error);

            alert(error.message || "Unable to open this plan.");

        }

    }


    /* =====================================
       HISTORY
    ===================================== */

    async function loadHistory() {

        loadAnalytics();

        showMessage(historyContent, "Loading your activity history...", "loading-message");

        try {

            const response = await apiRequest("/api/history");

            const history = response.history || [];

            historyContent.replaceChildren();

            if (history.length === 0) {

                showMessage(
                    historyContent,
                    "Your activity history is empty. Generate a fitness plan to get started!"
                );

                return;
            }

            history.forEach(item => {

                const card = document.createElement("div");
                card.className = "history-card";

                const heading = document.createElement("h3");

                heading.textContent =
                    `${formatText(item.plan_type || "Fitness")} Plan`;

                const goal = document.createElement("p");
                goal.textContent =
                    `Goal: ${formatText(item.goal || "—")}`;

                const level = document.createElement("p");
                level.textContent =
                    `Level: ${formatText(item.fitness_level || "—")}`;

                const duration = document.createElement("p");
                duration.textContent =
                    `Duration: ${item.duration ?? "—"} minutes`;

                const date = document.createElement("p");
                date.textContent =
                    `Date: ${formatDate(item.generated_at)}`;

                card.append(
                    heading,
                    goal,
                    level,
                    duration,
                    date
                );

                historyContent.appendChild(card);

            });

        } catch (error) {

            console.error("History error:", error);

            showMessage(
                historyContent,
                error.message || "Unable to load your history."
            );

        }

    }


    /* =====================================
       BMI CALCULATOR
    ===================================== */

    async function loadBMIProfileDetails() {

        try {

            const response = await apiRequest("/api/profile");

            const profile = response.profile || {};

            const heightInput = document.getElementById("bmiHeight");
            const weightInput = document.getElementById("bmiWeight");

            if (profile.height) {
                heightInput.value = profile.height;
            }

            if (profile.weight) {
                weightInput.value = profile.weight;
            }

        } catch (error) {

            console.warn("Unable to load profile details for BMI:", error);

        }

    }


    bmiForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const height = Number(
            document.getElementById("bmiHeight").value
        );

        const weight = Number(
            document.getElementById("bmiWeight").value
        );

        if (height <= 0 || weight <= 0) {

            showMessage(
                bmiResult,
                "Please enter valid height and weight."
            );

            bmiResult.hidden = false;
            return;

        }

        try {

            bmiResult.hidden = false;

            showMessage(
                bmiResult,
                "Calculating your BMI...",
                "loading-message"
            );

            const response = await apiRequest("/api/bmi", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    height: height,
                    weight: weight
                })
            });

            bmiResult.replaceChildren();

            const heading = document.createElement("h3");
            heading.textContent = "Your BMI Result";

            const value = document.createElement("strong");
            value.textContent = Number(response.bmi).toFixed(1);

            const category = document.createElement("p");
            category.textContent =
                `Category: ${formatText(response.category)}`;

            const note = document.createElement("small");
            note.textContent =
                "BMI is a screening measure, not a complete assessment of health.";

            bmiResult.append(heading, value, category, note);

        } catch (error) {

            console.error("BMI calculation error:", error);

            showMessage(
                bmiResult,
                error.message || "Unable to calculate BMI."
            );

            bmiResult.hidden = false;

        }

    });


    /* =====================================
       PROFILE - LOAD
    ===================================== */

    async function loadProfile() {

        profileMessage.textContent = "Loading profile...";

        try {

            const response = await apiRequest("/api/profile");

            const profile = response.profile || {};

            document.getElementById("profileName").value =
                profile.name ?? "";

            document.getElementById("profileAge").value =
                profile.age ?? "";

            if (document.getElementById("profileGender")) {
                document.getElementById("profileGender").value = profile.gender ?? "";
            }

            document.getElementById("profileHeight").value =
                profile.height ?? "";

            document.getElementById("profileWeight").value =
                profile.weight ?? "";

            document.getElementById("profileGoal").value =
                profile.fitness_goal || "general_fitness";

            document.getElementById("profileLevel").value =
                profile.fitness_level || "beginner";

            profileMessage.textContent = "";

        } catch (error) {

            console.error("Profile loading error:", error);

            profileMessage.textContent =
                error.message || "Unable to load your profile.";

        }

    }


    /* =====================================
       PROFILE - SAVE
    ===================================== */

    profileForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const profileData = {
            name: document.getElementById("profileName").value.trim(),

            age: document.getElementById("profileAge").value
                ? Number(document.getElementById("profileAge").value)
                : null,

            gender: document.getElementById("profileGender")?.value || null,

            height: document.getElementById("profileHeight").value
                ? Number(document.getElementById("profileHeight").value)
                : null,

            weight: document.getElementById("profileWeight").value
                ? Number(document.getElementById("profileWeight").value)
                : null,

            fitness_goal: document.getElementById("profileGoal").value,

            fitness_level: document.getElementById("profileLevel").value
        };

        const saveButton = profileForm.querySelector(
            'button[type="submit"]'
        );

        saveButton.disabled = true;
        saveButton.textContent = "Saving...";

        profileMessage.textContent = "";

        try {

            const response = await apiRequest("/api/profile", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(profileData)
            });

            profileMessage.textContent =
                response.message || "Profile saved successfully!";

        } catch (error) {

            console.error("Profile saving error:", error);

            profileMessage.textContent =
                error.message || "Unable to save your profile.";

        } finally {

            saveButton.disabled = false;
            saveButton.textContent = "Save Profile";

        }

    });


    /* =====================================
       DATE FORMATTING
    ===================================== */

    function formatDate(dateValue) {

        if (!dateValue) {
            return "Date unavailable";
        }

        const date = new Date(dateValue);

        if (Number.isNaN(date.getTime())) {
            return String(dateValue);
        }

        return date.toLocaleString();

    }


    /* =====================================
       INITIALIZATION
    ===================================== */

    hideSidebar();
    loadAnalytics();

    console.log(
        "FitFlow AI frontend initialized successfully."
    );

});
