// for account
document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('accountToggle');
    const dropdown = document.getElementById('accountMenu');

    toggleBtn.addEventListener('click', function (e) {
      e.stopPropagation(); // prevent bubbling
      dropdown.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function () {
      dropdown.classList.remove('show');
    });
  });




document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
  document.querySelector('section nav').classList.toggle('mobile-menu-open');
});



// popup
  // Auto-hide message after 3 seconds
  setTimeout(function () {
    const messages = document.querySelectorAll('.alert, .message, .flash-message');
    messages.forEach(msg => {
      msg.style.transition = 'opacity 0.5s ease';
      msg.style.opacity = '0';
      setTimeout(() => msg.style.display = 'none', 500);
    });
  }, 3000); // 3 seconds
// popup

// searchbar

  const searchInput = document.getElementById('searchInput');
  const autocompleteList = document.getElementById('autocompleteList');

  let timeout = null;

  searchInput.addEventListener('input', function() {
    clearTimeout(timeout);
    const query = this.value.trim();

    if (query.length < 2) {
      autocompleteList.style.display = 'none';
      autocompleteList.innerHTML = '';
      return;
    }

    timeout = setTimeout(() => {
      fetch(`/Core/api/search-books/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
          autocompleteList.innerHTML = '';
          if (data.length === 0) {
            autocompleteList.style.display = 'none';
            return;
          }

          data.forEach(book => {
            const item = document.createElement('div');
            item.classList.add('autocomplete-item');
            item.textContent = book.title + " by " + book.author;
            item.onclick = () => {
              window.location.href = `/Core/book/${book.id}/`;  // Redirect to book detail page
            };
            autocompleteList.appendChild(item);
          });
          autocompleteList.style.display = 'block';
        });
    }, 300); // debounce delay
  });

  // Hide autocomplete when clicking outside
  document.addEventListener('click', function(e) {
    if (!autocompleteList.contains(e.target) && e.target !== searchInput) {
      autocompleteList.style.display = 'none';
    }
  });


// quantity

//   document.addEventListener('click', async (e) => {
//   const btn = e.target.closest('.quantity-btn');
//   if (!btn) return;

//   const row   = btn.closest('tr');
//   const id    = row.dataset.itemId;               
//   const action = btn.dataset.action;              

//   const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

//   const res = await fetch(`/cart/update/${id}/`, {
//     method: 'POST',
//     headers: { 'X-CSRFToken': csrf },
//     body: new URLSearchParams({ action })
//   });
//   if (!res.ok) return;

//   const data = await res.json();

//   row.querySelector('.quantity-input').value = data.quantity;
//   row.querySelector('.item-subtotal').textContent = `$${data.itemSubtotal}`;
//   document.getElementById('cart-total').textContent = data.total;
// });


// quantity

document.addEventListener('DOMContentLoaded', function() {
    // Quantity adjustment buttons
    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.getAttribute('data-action');
            const itemId = this.getAttribute('data-item-id');
            const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            let quantity = parseInt(input.value);
            
            if (action === 'increase') {
                quantity += 1;
            } else if (action === 'decrease' && quantity > 1) {
                quantity -= 1;
            }
            
            input.value = quantity;
            updateCartItem(itemId, quantity);
        });
    });
    
    // Manual quantity input
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            let quantity = parseInt(this.value);
            
            if (isNaN(quantity) || quantity < 1) {
                quantity = 1;
                this.value = 1;
            }
            
            updateCartItem(itemId, quantity);
        });
    });
    
    // Update cart item via AJAX
    function updateCartItem(itemId, quantity) {
        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the item subtotal
                document.getElementById(`item-subtotal-${itemId}`).textContent = `$${data.item_total.toFixed(2)}`;
                
                // Update the cart summary
                document.querySelector('.summary-row.subtotal span:last-child').textContent = `$${data.subtotal.toFixed(2)}`;
                document.querySelector('.summary-row.total span:last-child').textContent = `$${data.total_price.toFixed(2)}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});


  