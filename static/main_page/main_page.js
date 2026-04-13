document.addEventListener('DOMContentLoaded', () => {
    
    // ====== 1. VIDEO BLUR ON SCROLL ======
    const heroVideo = document.getElementById('heroVideo');
    const heroSection = document.getElementById('hero');
    
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;
        const heroHeight = heroSection.offsetHeight;
        
        // Calculate blur based on scroll position
        // When scrollY exceeds heroHeight, blur increases
        const blurAmount = Math.max(0, (scrollY - heroHeight / 2) / 50);
        
        // Apply blur to video
        heroVideo.style.filter = `blur(${blurAmount}px)`;
    });

    // ====== 2. CUSTOM DROPDOWN LOGIC ======
    const trigger = document.getElementById('categoryTrigger');
    const menu = document.getElementById('categoryMenu');
    const selectedText = document.getElementById('selectedCategory');
    const items = document.querySelectorAll('.dropdown-item');

    // Toggle Menu
    trigger.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent immediate close
        trigger.classList.toggle('active');
        menu.classList.toggle('active');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!trigger.contains(e.target) && !menu.contains(e.target)) {
            trigger.classList.remove('active');
            menu.classList.remove('active');
        }
    });

    // Handle Selection
    items.forEach(item => {
        item.addEventListener('click', (e) => {
            // Find the link inside the dropdown item
            const link = item.querySelector('a');
            if (link) {
                // Navigate to the link's URL
                window.location.href = link.href;
            }
        });
    });

    // ====== 3. REVEAL ON SCROLL (Simple Observer) ======
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Select all product cards to animate
    const cards = document.querySelectorAll('.product-card-elite');
    cards.forEach((card, index) => {
        // Set initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`; // Staggered delay
        observer.observe(card);
    });
});