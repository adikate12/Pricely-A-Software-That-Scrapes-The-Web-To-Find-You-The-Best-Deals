// Define global functions first
let currentRecommendations = [];

window.viewDetails = function(productId) {
    console.log('View Details clicked for product:', productId);
    // Track the view details activity
    trackActivity('view_details', productId);
    
    // Find the product in the current recommendations
    const product = currentRecommendations.find(p => p.id === productId);
    if (product && product.link) {
        // Open the product link in a new tab
        window.open(product.link, '_blank');
    } else {
        console.error('Product link not found for ID:', productId);
        showToast('Unable to open product details. Please try again.');
    }
};

window.trackActivity = function(action, productId) {
    const userId = sessionStorage.getItem('userId') || 'anonymous';
    const email = sessionStorage.getItem('email') || 'anonymous';
    const username = sessionStorage.getItem('username') || 'Anonymous User';
    
    // Find the product in current recommendations
    const product = currentRecommendations.find(p => p.id === productId);
    
    fetch('../Login/track_interactions.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            email: email,
            username: username,
            action: action,
            product_id: productId,
            product_name: product?.name || '',
            brand: product?.brand || '',
            category: 'mobile',
            price: product?.price || 0,
            source: product?.source || 'unknown',
            page: window.location.pathname,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text().then(text => {
            try {
                return JSON.parse(text);
            } catch (e) {
                console.warn('Non-JSON response received:', text);
                return { status: 'success' };
            }
        });
    })
    .then(data => console.log('Activity tracked:', data))
    .catch(error => console.error('Error tracking activity:', error));
};

// Add showToast function at the top of the file
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Show the toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Remove the toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Add CSS for toast notifications
const style = document.createElement('style');
style.textContent = `
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #333;
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
        z-index: 1000;
    }
    .toast.show {
        opacity: 1;
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Get user info from session storage
    const userId = sessionStorage.getItem('userId') || 'anonymous';
    const username = sessionStorage.getItem('username') || 'Anonymous User';
    console.log('User ID:', userId);

    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const sections = document.querySelectorAll('.recommendation-section');
    console.log('Found tab buttons:', tabButtons.length);
    console.log('Found sections:', sections.length);

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log('Tab clicked:', button.dataset.type);
            // Remove active class from all buttons and sections
            tabButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.style.display = 'none');

            // Add active class to clicked button
            button.classList.add('active');

            // Show corresponding section
            const sectionId = `${button.dataset.type}-section`;
            document.getElementById(sectionId).style.display = 'block';

            // Load recommendations for the selected tab
            loadRecommendations(button.dataset.type);
        });
    });

    // Function to load recommendations
    async function loadRecommendations(type) {
        console.log('Loading recommendations for type:', type);
        const container = document.getElementById('recommendations-container');
        const loader = document.getElementById('recommendations-loader');
        
        // Show loader
        loader.style.display = 'block';
        container.innerHTML = '';

        try {
            console.log('Fetching recommendations...');
            const recommendations = await fetchRecommendations(type, userId, 8);
            console.log('Received recommendations:', recommendations);
            displayProducts(recommendations, container);
        } catch (error) {
            console.error(`Error loading ${type} recommendations:`, error);
            showToast('Error loading recommendations. Please try again later.');
        } finally {
            loader.style.display = 'none';
        }
    }

    // Function to fetch recommendations
    async function fetchRecommendations(type, userId, count = 8) {
        try {
            const email = sessionStorage.getItem('email') || 'anonymous';
            const response = await fetch(`../Login/recommendations.php?userId=${userId}&email=${email}&type=${type}&count=${count}`);
            if (!response.ok) {
                throw new Error('Failed to fetch recommendations');
            }
            const data = await response.json();
            return Array.isArray(data) ? data : data.recommendations;
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            showToast('Failed to load recommendations. Please try again later.');
            return [];
        }
    }

    // Function to display products in the grid
    function displayProducts(products, container) {
        if (!products || products.length === 0) {
            container.innerHTML = '<p class="no-products">No recommendations available at the moment.</p>';
            return;
        }

        // Store the current recommendations
        currentRecommendations = products;
        
        container.innerHTML = ''; // Clear existing content
        
        products.forEach(product => {
            console.log('Product:', product);
            console.log('Product ID:', product.id);
            console.log('Product Link:', product.link);
            
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <div class="product-image-container">
                    <img src="${product.image}" alt="${product.name}" class="product-image" onerror="this.src='../assets/Main_BG/iphone.jpg'">
                </div>
                <div class="product-details">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-price">${product.price_formatted}</p>
                    <div class="product-meta">
                        ${product.brand ? `<p class="product-brand">${product.brand}</p>` : ''}
                        <p class="product-source">${product.source}</p>
                    </div>
                    <div class="product-actions">
                        <button class="view-details-btn" data-product-id="${product.id}">View Details</button>
                    </div>
                </div>
            `;
            container.appendChild(productCard);
        });

        // Add event delegation for view details buttons
        container.addEventListener('click', function(event) {
            if (event.target.classList.contains('view-details-btn')) {
                const productId = event.target.getAttribute('data-product-id');
                console.log('View Details clicked for product:', productId);
                viewDetails(productId);
            }
        });
    }

    // Load initial recommendations
    console.log('Loading initial recommendations');
    loadRecommendations('personalized');
});

// Helper functions for product actions
function addToCart(productId) {
    console.log('Adding to cart:', productId);
    // Track the add to cart activity
    trackActivity('add_to_cart', productId);
} 