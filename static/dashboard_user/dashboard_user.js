document.addEventListener('DOMContentLoaded', () => {

    // 1. GREETING BASED ON TIME
    const greetingTitle = document.getElementById('greetingTitle');
    const hour = new Date().getHours();
    let timeGreeting = "Welcome";

    if (hour < 12) {
        timeGreeting = "Good Morning";
    } else if (hour < 18) {
        timeGreeting = "Good Afternoon";
    } else {
        timeGreeting = "Good Evening";
    }

    if (greetingTitle) {
        const originalText = greetingTitle.textContent;
        greetingTitle.textContent = originalText.replace("Welcome", timeGreeting);
    }

    // 2. STAT CARDS
    const cards = document.querySelectorAll('.stat-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const xRotation = -((y - rect.height / 2) / 25);
            const yRotation = (x - rect.width / 2) / 25;

            card.style.transform = `perspective(600px) rotateX(${xRotation}deg) rotateY(${yRotation}deg) translateZ(10px)`;
            card.style.boxShadow = '0 25px 50px rgba(212, 163, 115, 0.2)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(600px) rotateX(0) rotateY(0) translateZ(0)';
            card.style.boxShadow = '0 15px 35px rgba(212, 163, 115, 0.15)';
        });
    });

    // 3. AJAX SECTION SWITCHING
    const navLinks = document.querySelectorAll('.dash-nav-link');
    const sections = document.querySelectorAll('.dashboard-section');

    function switchSection(sectionId) {
        navLinks.forEach(l => l.classList.remove('active'));
        sections.forEach(s => {
            s.style.display = 'none';
            s.classList.remove('active', 'fade-in-up');
        });

        const targetLink = document.querySelector(`[data-section="${sectionId}"]`);
        const targetSection = document.getElementById(`${sectionId}-section`);

        if (targetSection) {
            targetSection.style.display = 'block';
            setTimeout(() => {
                targetSection.classList.add('active', 'fade-in-up');
            }, 10);
        }

        if (targetLink) targetLink.classList.add('active');
        sessionStorage.setItem('activeDashboardSection', sectionId);
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.classList.contains('sign-out-link')) {
            return;
        }

            preventPageJump(e);  // Use shared utility
            const sectionId = link.getAttribute('data-section');
            if (sectionId) switchSection(sectionId);
        });
    });

    const urlParams = new URLSearchParams(window.location.search);
    const initialSection = urlParams.get('section') || sessionStorage.getItem('activeDashboardSection') || 'overview';

    switchSection(initialSection);

    // 5. PASSWORD TOGGLE FOR INFORMATION SECTION
    const togglePasswordBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                togglePasswordBtn.textContent = 'Hide';
                togglePasswordBtn.style.background = 'var(--accent-sand)';
                togglePasswordBtn.style.borderColor = 'var(--accent-sand)';
            } else {
                passwordInput.type = 'password';
                togglePasswordBtn.textContent = 'Show';
                togglePasswordBtn.style.background = 'var(--primary-charcoal)';
                togglePasswordBtn.style.borderColor = 'var(--primary-charcoal)';
            }
        });
    }
});

function calculateTotal() {
    const checkboxes = document.querySelectorAll('.product-checkbox:checked');
    let total = 0;
    let totalItems = 0;

    checkboxes.forEach(cb => {
        const price = parseFloat(cb.getAttribute('data-price'));
        const qty = parseInt(cb.getAttribute('data-qty')); 
        
        total += (price * qty); 
        totalItems += qty;
    });

    // Default to USD
    let displayTotal = total;
    let currencySymbol = '$';

    // If variables from template indicate INR, convert
    if (typeof CURRENT_CURRENCY !== 'undefined' && typeof EXCHANGE_RATE !== 'undefined') {
        if (CURRENT_CURRENCY === 'INR') {
            displayTotal = total * EXCHANGE_RATE;
            currencySymbol = '₹';
        }
    }

    // Format output
    const formattedTotal = displayTotal.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    document.getElementById('total-price').textContent = `${currencySymbol}${formattedTotal}`;
    document.getElementById('selected-count').textContent = totalItems;
}

function deleteCartItem(itemId) {
    fetch(`/delete-cart-item/${itemId}`, { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const element = document.getElementById(`cart-item-${itemId}`);
            element.style.transition = "all 0.5s ease";
            element.style.opacity = "0";
            element.style.transform = "translateX(30px)";
            
            setTimeout(() => {
                element.remove();
                calculateTotal();
            }, 500);
        }
    });
}

//mMy order//
function processCheckout() {
    const selectedCheckboxes = document.querySelectorAll('.product-checkbox:checked');
    if (selectedCheckboxes.length === 0) {
        alert("Please select at least one item to checkout!");
        return;
    }

    const cartItemIds = Array.from(selectedCheckboxes).map(cb => {
        const cartItemRow = cb.closest('.cart-item-row');
        return cartItemRow ? cartItemRow.id.replace('cart-item-', '') : null;
    }).filter(id => id !== null);

    if (confirm("Do you want to proceed to checkout?")) {
        fetch('/checkout', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ cart_item_ids: cartItemIds })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error('Network response was not ok');
            }
            return res.json();
        })
        .then(data => {
            if (data.success) {
                alert(data.message);
                setTimeout(() => {
                    window.location.href = window.location.pathname + '?section=orders';
                }, 1500);
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred during checkout. Please try again.");
        });
    }
}