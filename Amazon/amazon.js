document.addEventListener('DOMContentLoaded', () => {
    // Fetch product data from your JSON file
    fetch('amazon_products.json')
      .then(response => response.json())
      .then(data => {
        const productGrid = document.querySelector('.product-grid');
        const noResults = document.querySelector('.no-results');

        // Create product cards and append them to the grid
        data.forEach((product) => {
          const productCard = document.createElement('div');
          productCard.classList.add('product-card');

          productCard.innerHTML = `
            <img src="${product['Image URL']}" alt="${product['Product Name']}">
            <h2>${product['Product Name']}</h2>
            <a href="#" class="price-box">₹${product['Price']}</a>
          `;

          productGrid.appendChild(productCard);
        });

        // Search functionality
        const searchInput = document.querySelector('.search-input');
        searchInput.addEventListener('keyup', () => {
          const searchTerm = searchInput.value.trim().toLowerCase();

          const productCards = document.querySelectorAll('.product-card');
          let found = false;
          productCards.forEach((card) => {
            const productName = card.querySelector('h2').textContent.toLowerCase();
            if (productName.includes(searchTerm)) {
              card.style.display = 'block';
              found = true;
            } else {
              card.style.display = 'none';
            }
          });

          if (found) {
            noResults.style.display = 'none';
          } else {
            noResults.style.display = 'block';
          }
        });
      })
      .catch(error => console.error('Error fetching data:', error));
  });