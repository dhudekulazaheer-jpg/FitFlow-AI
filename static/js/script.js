
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

        const response = await fetch(url, options);

        let data;

        try {
            data = await response.json();
        } catch {
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok || data.success === false) {
            throw new Error(
                data.error || data.message || "Something went wrong."
            );
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
            body_part: formData.get("body_part") || null
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

            const errorBox = document.createElement("div");
            errorBox.className = "error-message";
            errorBox.textContent =
                error.message || "Unable to generate your plan.";

            planContent.replaceChildren(errorBox);

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

        const details = document.createElement("p");

        details.textContent =
            `Goal: ${formatText(result.goal || "—")} | ` +
            `Level: ${formatText(result.fitness_level || "—")} | ` +
            `Duration: ${result.requested_duration_minutes ?? "—"} minutes`;

        planSummary.append(heading, details);

        const components = [
            { title: "Yoga Routine", key: "yoga" },
            { title: "Workout Routine", key: "workout" }
        ];

        let displayed = false;

        components.forEach(component => {

            const plan = result[component.key];

            if (plan && typeof plan === "object") {

                renderSection(component.title, plan);
                displayed = true;

            }

        });

        if (!displayed) {
            renderSection("Your Fitness Routine", result);
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

    console.log(
        "FitFlow AI frontend initialized successfully."
    );

});
