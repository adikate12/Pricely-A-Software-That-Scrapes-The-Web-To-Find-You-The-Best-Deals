document.addEventListener('DOMContentLoaded', function() {
    const menu = document.querySelector('#menu-icon');
    const navlist = document.querySelector('.navlist');

    menu.onclick = () => {
        menu.classList.toggle('bx-x');
        navlist.classList.toggle('open');
    };

    window.onscroll = () => {
        menu.classList.remove('bx-x');
        navlist.classList.remove('open');
    };

    /* Offers Sliding Panel Starts */
    let currentIndex = 0;
    let banners = [];
    let dots = [];
    let isTransitioning = false;

    fetch('offer.json')
        .then(response => response.json())
        .then(data => {
            banners = data;
            const bannerContainer = document.getElementById('bannerContainer');
            const dotsContainer = document.getElementById('dotsContainer');

            banners.forEach((offer, index) => {
                const bannerCard = document.createElement('div');
                bannerCard.classList.add('banner-card');

                const anchor = document.createElement('a');
                anchor.href = offer["Product Link"];
                anchor.target = "_blank";

                const img = document.createElement('img');
                img.src = offer["Image Source"];
                img.alt = offer["Alt Text"];
                img.onerror = function() {
                    this.src = 'path/to/your/default-placeholder-image.jpg';
                };

                anchor.appendChild(img);
                bannerCard.appendChild(anchor);
                bannerContainer.appendChild(bannerCard);

                const dot = document.createElement('span');
                dot.classList.add('dot');
                dot.addEventListener('click', () => goToSlide(index));
                dotsContainer.appendChild(dot);
                dots.push(dot);
            });

            const firstClone = bannerContainer.firstElementChild.cloneNode(true);
            bannerContainer.appendChild(firstClone);
            dots[0].classList.add('active');
            setInterval(nextSlide, 5000);
        })
        .catch(error => console.error('Error loading the offer banners:', error));

    function nextSlide() {
        if (isTransitioning) return;
        isTransitioning = true;
        currentIndex++;
        updateBannerPosition();

        if (currentIndex === banners.length) {
            setTimeout(() => {
                bannerContainer.style.transition = 'none';
                currentIndex = 0;
                updateBannerPosition();
                setTimeout(() => {
                    bannerContainer.style.transition = 'transform 0.7s ease';
                    isTransitioning = false;
                }, 20);
            }, 700);
        } else {
            setTimeout(() => isTransitioning = false, 700);
        }
    }

    function prevSlide() {
        if (isTransitioning) return;
        isTransitioning = true;
        currentIndex--;
        if (currentIndex < 0) {
            bannerContainer.style.transition = 'none';
            currentIndex = banners.length - 1;
            updateBannerPosition();
            setTimeout(() => {
                bannerContainer.style.transition = 'transform 0.7s ease';
                isTransitioning = false;
            }, 20);
        } else {
            updateBannerPosition();
            setTimeout(() => isTransitioning = false, 700);
        }
    }

    function updateBannerPosition() {
        const bannerContainer = document.getElementById('bannerContainer');
        bannerContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
        dots.forEach(dot => dot.classList.remove('active'));
        if (currentIndex < banners.length) {
            dots[currentIndex].classList.add('active');
        }
    }

    function goToSlide(index) {
        if (isTransitioning) return;
        currentIndex = index;
        updateBannerPosition();
    }

    document.getElementById('nextArrow').addEventListener('click', nextSlide);
    document.getElementById('prevArrow').addEventListener('click', prevSlide);

    /* Offers Sliding Panel Ends */

    /* News Fetching */
    const apiKey = '11c9015e1471424b9b641b9b8364b424';
    const url = `https://newsapi.org/v2/everything?q=smartphone&apiKey=${apiKey}`;
    let displayedArticles = new Set();

    function fetchSmartphoneNews() {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const articles = data.articles.filter(article =>
                    !displayedArticles.has(article.title) &&
                    article.title.toLowerCase().includes('smartphone')
                ).slice(0, 8);

                articles.forEach(article => displayedArticles.add(article.title));
                displayNews(articles);
            })
            .catch(error => console.error('Error fetching smartphone news:', error));
    }

    function displayNews(articles) {
        const newsContainer = document.getElementById('news-container');
        newsContainer.innerHTML = '';

        articles.forEach(article => {
            const newsItem = document.createElement('div');
            newsItem.innerHTML = `
                <a href="${article.url}" target="_blank" style="text-decoration: none; color: inherit;">
                    <h3>${article.title}</h3>
                    <img src="${article.urlToImage}" alt="News image" />
                    <p>${article.description}</p>
                </a>
            `;
            newsContainer.appendChild(newsItem);
        });
    }

    fetchSmartphoneNews();
    setInterval(fetchSmartphoneNews, 60000);

    /* Side Drawer Menu */
    const menuButton = document.getElementById('menu-button');
    const closeButton = document.getElementById('close-button');
    const sideDrawer = document.getElementById('side-drawer');
    const overlay = document.getElementById('overlay');

    menuButton.addEventListener('click', () => {
        sideDrawer.style.width = '250px';
        overlay.classList.add('open');
    });

    closeButton.addEventListener('click', () => {
        sideDrawer.style.width = '0';
        overlay.classList.remove('open');
    });

    overlay.addEventListener('click', () => {
        sideDrawer.style.width = '0';
        overlay.classList.remove('open');
    });

    // Add recommendation button handler
    const recommendationBtn = document.getElementById('recommendation-btn');
    if (recommendationBtn) {
        recommendationBtn.addEventListener('click', function() {
            // Get user info from session storage
            const userId = sessionStorage.getItem('userId') || 'anonymous';
            const username = sessionStorage.getItem('username') || 'Anonymous User';
            
            // Redirect to the recommendation page
            window.location.href = 'recommendations.html';
        });
    }
});
