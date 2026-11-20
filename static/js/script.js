/*
 * script.js
 * ---------
 * Small, beginner-friendly JavaScript file.
 * Its only job on the seat-selection page is to:
 *   1. Toggle a "selected" look when a seat checkbox is clicked.
 *   2. Update the running total (seat count + amount) on screen.
 *   3. Enable the "Confirm Booking" button once at least one seat
 *      is selected.
 *
 * This file does NOT talk to the server directly - the actual
 * booking is submitted normally through the HTML <form> in
 * seats.html when the user clicks "Confirm Booking".
 */

document.addEventListener("DOMContentLoaded", function () {
    const checkboxes = document.querySelectorAll(".seat-checkbox");
    const selectedTextEl = document.getElementById("selected-seats-text");
    const selectedCountEl = document.getElementById("selected-seats-count");
    const selectedTotalEl = document.getElementById("selected-seats-total");
    const confirmBtn = document.getElementById("confirm-booking-btn");

    // If this page has no seat checkboxes, there's nothing to do
    // (e.g. we're not on the seat-selection page).
    if (checkboxes.length === 0) {
        return;
    }

    function updateSummary() {
        const checked = Array.from(checkboxes).filter((cb) => cb.checked);

        // Toggle the visual "selected" class on each seat label
        checkboxes.forEach((cb) => {
            const seatLabelEl = cb.closest(".seat");
            if (cb.checked) {
                seatLabelEl.classList.add("seat-selected");
            } else {
                seatLabelEl.classList.remove("seat-selected");
            }
        });

        const labels = checked.map((cb) => cb.dataset.label);
        const count = checked.length;
        const total = count * (typeof SEAT_PRICE !== "undefined" ? SEAT_PRICE : 0);

        selectedTextEl.textContent = labels.length > 0 ? labels.join(", ") : "None";
        selectedCountEl.textContent = count;
        selectedTotalEl.textContent = total.toFixed(2);

        confirmBtn.disabled = count === 0;
    }

    checkboxes.forEach((cb) => {
        cb.addEventListener("change", updateSummary);
    });

    // Set the initial state when the page loads.
    updateSummary();
});
