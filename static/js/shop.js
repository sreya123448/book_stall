document.addEventListener('DOMContentLoaded', function() {
    // Price range filter
    const priceRange = document.getElementById('priceRange');
    if (priceRange) {
        priceRange.addEventListener('input', function() {
            const maxPrice = this.value;
            filterBooks();
        });
    }

    // Category filter
    const categoryCheckboxes = document.querySelectorAll('input[name="category"]');
    categoryCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterBooks);
    });

    // Availability filter
    const availabilityCheckbox = document.querySelector('input[name="availability"]');
    if (availabilityCheckbox) {
        availabilityCheckbox.addEventListener('change', filterBooks);
    }

    // Sort select
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            window.location.href = `?sort=${sortValue}`;
        });
    }

    // Reset filters
    const resetFiltersBtn = document.querySelector('.reset-filters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            // Reset all checkboxes
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Reset price range
            if (priceRange) priceRange.value = 1000;
            
            // Reset sort
            if (sortSelect) sortSelect.value = 'price_asc';
            
            filterBooks();
        });
    }

    // Quick view modal
    const quickViewBtns = document.querySelectorAll('.quick-view-btn');
    const modal = document.getElementById('quickViewModal');
    const closeModal = document.querySelector('.close-modal');
    
    if (quickViewBtns && modal) {
        quickViewBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const bookCard = this.closest('.book-card');
                const bookId = bookCard.dataset.bookId; // You'll need to add data-book-id to your book cards
                
                // Fetch book details via AJAX
                fetch(`/books/${bookId}/quick-view/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('quickViewContent').innerHTML = `
                                <div class="quick-view-container">
                                    <div class="quick-view-image">
                                        <img src="${data.book.cover_image}" alt="${data.book.title}">
                                    </div>
                                    <div class="quick-view-details">
                                        <h2>${data.book.title}</h2>
                                        <p class="author">by ${data.book.author}</p>
                                        <p class="price">$${data.book.price}</p>
                                        <p class="description">${data.book.description}</p>
                                        <div class="quick-view-actions">
                                            <button class="add-to-cart">Add to Cart</button>
                                            <button class="add-to-wishlist">Add to Wishlist</button>
                                        </div>
                                    </div>
                                </div>
                            `;
                            modal.style.display = 'block';
                        }
                    });
            });
        });
        
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                modal.style.display = 'none';
            });
        }
        
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Filter books function (AJAX implementation)
    function filterBooks() {
        const maxPrice = priceRange ? priceRange.value : 1000;
        const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked')).map(cb => cb.value);
        const inStockOnly = availabilityCheckbox ? availabilityCheckbox.checked : false;
        
        // You would typically make an AJAX call here to your Django view
        // with these filter parameters and update the book grid
        
        console.log('Filters applied:', {
            maxPrice,
            selectedCategories,
            inStockOnly
        });
        
        // For a real implementation, you would use fetch() to call your Django view
        // and update the book grid with the response
    }
});


// for dropdown
document.querySelector('.account-btn').addEventListener('click', function(e) {
  if (window.innerWidth <= 768) { // Mobile breakpoint
    e.preventDefault();
    const menu = this.closest('.account-dropdown').querySelector('.dropdown-menu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
  }
});

// for dropdown