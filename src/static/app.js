document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function buildParticipantItem(email, activityName, card) {
    const li = document.createElement("li");
    li.className = "participant-item";

    const span = document.createElement("span");
    span.textContent = email;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-participant";
    deleteBtn.title = `Remove ${email}`;
    deleteBtn.setAttribute("aria-label", `Remove ${email}`);
    deleteBtn.textContent = "✕";

    deleteBtn.addEventListener("click", async () => {
      deleteBtn.disabled = true;
      try {
        const res = await fetch(
          `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
          { method: "DELETE" }
        );
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || "Failed to remove participant.");
          deleteBtn.disabled = false;
          return;
        }

        // Update spots count
        const spotsEl = card.querySelector(".spots-count");
        const spotsParent = card.querySelector(".spots");
        const newSpots = parseInt(spotsEl.textContent, 10) + 1;
        spotsEl.textContent = newSpots;
        const maxSpots = parseInt(spotsParent.textContent.match(/\/\s*(\d+)/)[1], 10);
        spotsParent.className = newSpots === 0 ? "spots spots-full" : newSpots <= 3 ? "spots spots-low" : "spots";

        // Remove the row
        const list = li.closest(".participants-list");
        li.remove();

        // Show placeholder when empty
        if (list.querySelectorAll(".participant-item").length === 0) {
          list.innerHTML = `<li class="no-participants">No participants yet</li>`;
        }

        // Update toggle count
        const toggleBtn = card.querySelector(".toggle-participants");
        const count = list.querySelectorAll(".participant-item").length;
        toggleBtn.innerHTML = `<span class="toggle-icon">${toggleBtn.querySelector(".toggle-icon").textContent}</span> Participants (${count})`;
      } catch {
        alert("Network error. Please try again.");
        deleteBtn.disabled = false;
      }
    });

    li.appendChild(span);
    li.appendChild(deleteBtn);
    return li;
  }

  function buildActivityCard(name, details) {
    const card = document.createElement("div");
    card.className = "activity-card";
    card.dataset.activity = name;

    const spotsLeft = details.max_participants - details.participants.length;
    const spotsClass = spotsLeft === 0 ? "spots spots-full" : spotsLeft <= 3 ? "spots spots-low" : "spots";

    card.innerHTML = `
      <h4>${name}</h4>
      <p class="activity-description">${details.description}</p>
      <p><strong>Schedule:</strong> ${details.schedule}</p>
      <p class="${spotsClass}"><strong>Availability:</strong> <span class="spots-count">${spotsLeft}</span> / ${details.max_participants} spots left</p>
      <button class="toggle-participants" aria-expanded="true">
        <span class="toggle-icon">▼</span> Participants (${details.participants.length})
      </button>
      <div class="participants-panel">
        <ul class="participants-list"></ul>
      </div>
    `;

    const list = card.querySelector(".participants-list");
    if (details.participants.length) {
      details.participants.forEach(p => list.appendChild(buildParticipantItem(p, name, card)));
    } else {
      list.innerHTML = `<li class="no-participants">No participants yet</li>`;
    }

    card.querySelector(".toggle-participants").addEventListener("click", () => {
      const btn = card.querySelector(".toggle-participants");
      const panel = card.querySelector(".participants-panel");
      const expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!expanded));
      btn.querySelector(".toggle-icon").textContent = expanded ? "▶" : "▼";
      panel.hidden = expanded;
    });

    return card;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        activitiesList.appendChild(buildActivityCard(name, details));

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Update the matching activity card in-place
        const card = activitiesList.querySelector(`[data-activity="${activity}"]`);
        if (card) {
          const spotsEl = card.querySelector(".spots-count");
          const spotsParent = card.querySelector(".spots");
          const toggleBtn = card.querySelector(".toggle-participants");
          const list = card.querySelector(".participants-list");

          const currentSpots = parseInt(spotsEl.textContent, 10);
          const newSpots = Math.max(0, currentSpots - 1);
          spotsEl.textContent = newSpots;

          spotsParent.className = newSpots === 0 ? "spots spots-full" : newSpots <= 3 ? "spots spots-low" : "spots";

          // Append new participant
          const placeholder = list.querySelector(".no-participants");
          if (placeholder) placeholder.remove();
          list.appendChild(buildParticipantItem(email.trim().toLowerCase(), activity, card));

          // Update toggle button count
          const count = list.querySelectorAll("li").length;
          toggleBtn.innerHTML = `<span class="toggle-icon">${toggleBtn.querySelector(".toggle-icon").textContent}</span> Participants (${count})`;
        }

        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
