// const container = document.getElementById('container');
// const overlayCon = document.getElementById('overlayCon');
// const overlayBtn = document.getElementById('overlayBtn');
// const signInButton = document.getElementById('signIn');
// const signUpButton = document.getElementById('signUp');

// // Event listener for overlay button (for toggling the right-panel-active class)
// overlayBtn.addEventListener('click', () => {
//     container.classList.toggle('right-panel-active');

//     // Remove scaling class, and add it back for smooth animation
//     overlayBtn.classList.remove('btnScaled');
//     window.requestAnimationFrame(() => {
//         overlayBtn.classList.add('btnScaled');
//     });
// });

// // Event listener for sign-in button (brings the user back to the sign-in form)
// signInButton.addEventListener('click', () => {
//     container.classList.remove('right-panel-active');

//     // Same effect for overlayBtn, you can add additional animations if needed
//     overlayBtn.classList.remove('btnScaled');
//     window.requestAnimationFrame(() => {
//         overlayBtn.classList.add('btnScaled');
//     });
// });

// // Event listener for sign-up button (shows the sign-up form)
// signUpButton.addEventListener('click', () => {
//     container.classList.add('right-panel-active');

//     // Scaling effect for button
//     overlayBtn.classList.remove('btnScaled');
//     window.requestAnimationFrame(() => {
//         overlayBtn.classList.add('btnScaled');
//     });
// });




const container = document.getElementById('container');
const overlayCon = document.getElementById('overlayCon');
const overlayBtn = document.getElementById('overlayBtn');
const signInButton = document.getElementById('signIn');
const signUpButton = document.getElementById('signUp');

// Event listener for overlay button (for toggling the right-panel-active class)
overlayBtn.addEventListener('click', () => {
    container.classList.toggle('right-panel-active');

    // Remove scaling class, and add it back for smooth animation
    overlayBtn.classList.remove('btnScaled');
    window.requestAnimationFrame(() => {
        overlayBtn.classList.add('btnScaled');
    });
    
    // Track this interaction if tracker is initialized
    if (window.activityTracker) {
        window.activityTracker.sendActivity('toggle_login_panel', window.location.pathname, {
            element: 'overlayBtn',
            newState: container.classList.contains('right-panel-active') ? 'signup' : 'signin'
        });
    }
});

// Event listener for sign-in button (brings the user back to the sign-in form)
signInButton.addEventListener('click', () => {
    container.classList.remove('right-panel-active');

    // Same effect for overlayBtn, you can add additional animations if needed
    overlayBtn.classList.remove('btnScaled');
    window.requestAnimationFrame(() => {
        overlayBtn.classList.add('btnScaled');
    });
    
    // Track this interaction if tracker is initialized
    if (window.activityTracker) {
        window.activityTracker.sendActivity('switch_to_signin', window.location.pathname, {
            element: 'signInButton'
        });
    }
});

// Event listener for sign-up button (shows the sign-up form)
signUpButton.addEventListener('click', () => {
    container.classList.add('right-panel-active');

    // Scaling effect for button
    overlayBtn.classList.remove('btnScaled');
    window.requestAnimationFrame(() => {
        overlayBtn.classList.add('btnScaled');
    });
    
    // Track this interaction if tracker is initialized
    if (window.activityTracker) {
        window.activityTracker.sendActivity('switch_to_signup', window.location.pathname, {
            element: 'signUpButton'
        });
    }
});