document.addEventListener('DOMContentLoaded', () => {
    fetch('reliance_data.json') // Ensure the correct path to your JSON file
        .then(response => response.json())
        .then(data => {
            const productGrid = document.querySelector('.product-grid');
            
            data.forEach((product, index) => {
                const productCard = document.createElement('div');
                productCard.classList.add('product-card');
                
                productCard.innerHTML = `
                    <img src="${product['Image URL']}" alt="${product['Product Name']}">
                     <h2>${product['Product Name']}</h2>
                     <a href="#" class="price" data-product-name="${product['Product Name']}">₹${product['Price']}</a>`;


                // Set initial opacity and transform for animation
                productCard.style.opacity = 0;
                productCard.style.transform = 'translateY(20px)'; // Starts slightly below its final position

                productGrid.appendChild(productCard);

                // Animate the product card fade-in and slide-up
                setTimeout(() => {
                    productCard.style.transition = 'opacity 0.6s ease-in-out, transform 0.6s ease-in-out';
                    productCard.style.opacity = 1;
                    productCard.style.transform = 'translateY(0)'; // Moves to its final position
                }, index * 150); // Stagger the animation for each card

                // Add hover effect for scaling up and glowing shadow
                productCard.addEventListener('mouseover', () => {
                    productCard.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
                    productCard.style.transform = 'scale(1.05)'; // Scale up the card slightly
                    productCard.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.3)'; // Add a shadow
                });

                productCard.addEventListener('mouseout', () => {
                    productCard.style.transform = 'scale(1)'; // Revert to original size
                    productCard.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)'; // Original shadow
                });

                // Handle price button click
                const priceButton = productCard.querySelector('.price');
                priceButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    // Handle click logic here (e.g., redirect to the product page)
                    alert(`Clicked on price for: ${priceButton.dataset.productName}`);
                });
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});
