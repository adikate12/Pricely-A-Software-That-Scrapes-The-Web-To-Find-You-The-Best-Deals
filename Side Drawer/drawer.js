const menuButton = document.getElementById('menu-button');
const closeButton = document.getElementById('close-button');
const sideDrawer = document.getElementById('side-drawer');
const overlay = document.getElementById('overlay');

// Function to open the side drawer
menuButton.addEventListener('click', () => {
    sideDrawer.style.width = '250px'; // Open the side drawer
    overlay.classList.add('open'); // Show the overlay
});

// Function to close the side drawer
closeButton.addEventListener('click', () => {
    sideDrawer.style.width = '0'; // Close the side drawer
    overlay.classList.remove('open'); // Hide the overlay
});

// Close the side drawer when clicking the overlay
overlay.addEventListener('click', () => {
    sideDrawer.style.width = '0'; // Close the side drawer
    overlay.classList.remove('open'); // Hide the overlay
});
